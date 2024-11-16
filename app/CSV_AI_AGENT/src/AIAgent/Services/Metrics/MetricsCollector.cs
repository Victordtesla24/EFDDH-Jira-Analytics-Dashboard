using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Linq;
using Microsoft.Extensions.Logging;
using AIAgent.Models;

namespace AIAgent.Services;

public class MetricsCollector : IMetricsCollector
{
    private readonly ILogger<MetricsCollector> _logger;
    private const double BytesToMb = 1024 * 1024;
    private SystemMetrics? _lastMetrics;
    private readonly SemaphoreSlim _semaphore = new(1, 1);
    private DateTime _lastCollectionTime = DateTime.MinValue;
    private readonly Process _process = Process.GetCurrentProcess();
    private Dictionary<string, double> _lastJiraMetrics = new();

    public MetricsCollector(ILogger<MetricsCollector> logger)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<SystemMetrics> CollectMetricsAsync(CancellationToken cancellationToken = default)
    {
        try
        {
            if (_lastMetrics != null && (DateTime.UtcNow - _lastCollectionTime).TotalSeconds < 1)
            {
                return _lastMetrics;
            }

            await _semaphore.WaitAsync(cancellationToken);
            try
            {
                _lastMetrics = new SystemMetrics
                {
                    MemoryUsageMb = _process.WorkingSet64 / BytesToMb,
                    CpuTimeMs = _process.TotalProcessorTime.TotalMilliseconds,
                    ThreadCount = _process.Threads.Count,
                    UptimeMinutes = (DateTime.Now - _process.StartTime).TotalMinutes,
                    Status = DetermineStatus(),
                    JiraMetrics = _lastJiraMetrics
                };
                _lastCollectionTime = DateTime.UtcNow;

                LogMetrics(_lastMetrics);
                return _lastMetrics;
            }
            finally
            {
                _semaphore.Release();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error collecting system metrics");
            return new SystemMetrics 
            { 
                Status = "Error",
                Error = ex.Message
            };
        }
    }

    private string DetermineStatus()
    {
        if (_process.WorkingSet64 / BytesToMb > 200) return "Warning";
        if (_process.Threads.Count > 50) return "Warning";
        return "Healthy";
    }

    public void UpdateJiraMetrics(Dictionary<string, double> metrics)
    {
        _lastJiraMetrics = metrics;
    }

    public Dictionary<string, double> ConvertToDictionary(SystemMetrics metrics)
    {
        ArgumentNullException.ThrowIfNull(metrics);
        var result = new Dictionary<string, double>
        {
            { "memory_usage_mb", metrics.MemoryUsageMb },
            { "cpu_time_ms", metrics.CpuTimeMs },
            { "thread_count", metrics.ThreadCount },
            { "uptime_minutes", metrics.UptimeMinutes }
        };

        foreach (var (key, value) in metrics.JiraMetrics)
        {
            result[$"jira_{key}"] = value;
        }

        return result;
    }

    private void LogMetrics(SystemMetrics metrics)
    {
        _logger.LogInformation(
            "System Metrics - Memory: {MemoryMB}MB, CPU: {CPUMs}ms, Threads: {ThreadCount}, Uptime: {Uptime}min",
            Math.Round(metrics.MemoryUsageMb, 2),
            Math.Round(metrics.CpuTimeMs, 2),
            metrics.ThreadCount,
            Math.Round(metrics.UptimeMinutes, 2)
        );

        // Log JIRA metrics if present
        if (metrics.JiraMetrics.Any())
        {
            var jiraMetricsStr = string.Join(", ",
                metrics.JiraMetrics.Select(kvp => $"{kvp.Key}: {kvp.Value}"));
            _logger.LogDebug("JIRA Metrics - {Metrics}", jiraMetricsStr);
        }

        // Log status changes
        if (_lastMetrics?.Status != metrics.Status)
        {
            _logger.LogInformation("System Status changed from {OldStatus} to {NewStatus}",
                _lastMetrics?.Status ?? "Unknown",
                metrics.Status);
        }
    }
}

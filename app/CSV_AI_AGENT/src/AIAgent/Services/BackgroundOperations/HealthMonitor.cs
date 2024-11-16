// src/AIAgent/Services/BackgroundOperations/HealthMonitor.cs
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using AIAgent.Services;

namespace AIAgent.Services.BackgroundOperations;

public class HealthMonitor : BaseBackgroundService
{
    private readonly IMetricsCollector _metricsCollector;
    private readonly StateManager _stateManager;

    public HealthMonitor(
        ILogger<HealthMonitor> logger,
        IMetricsCollector metricsCollector,
        StateManager stateManager,
        ErrorHandler errorHandler)
        : base(logger, TimeSpan.FromMinutes(1), errorHandler)
    {
        _metricsCollector = metricsCollector;
        _stateManager = stateManager;
    }

    public override async Task ExecuteOperationAsync(CancellationToken stoppingToken)
    {
        var metrics = await _metricsCollector.CollectMetricsAsync(stoppingToken);
        if (metrics.IsHealthy)
        {
            await _stateManager.UpdateState("Healthy", _metricsCollector.ConvertToDictionary(metrics));
        }
        else
        {
            await _stateManager.UpdateState("Unhealthy", _metricsCollector.ConvertToDictionary(metrics));
        }
    }
}
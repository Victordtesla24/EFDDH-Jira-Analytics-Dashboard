using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;
using AIAgent.Models;
using AIAgent.Services;

namespace AIAgent.Services.BackgroundOperations;

public sealed class SystemResourceOptimizer : BaseBackgroundService
{
    private const long MemoryThresholdBytes = 100_000_000; // Lower to 100MB
    private const double CpuThresholdMs = 500; // Add CPU threshold
    private readonly StateManager _stateManager;
    private readonly IMetricsCollector _metricsCollector;

    public SystemResourceOptimizer(
        ILogger<SystemResourceOptimizer> logger,
        StateManager stateManager,
        ErrorHandler errorHandler,
        IMetricsCollector metricsCollector)
        : base(logger, TimeSpan.FromMinutes(15), errorHandler)
    {
        _stateManager = stateManager ?? throw new ArgumentNullException(nameof(stateManager));
        _metricsCollector = metricsCollector ?? throw new ArgumentNullException(nameof(metricsCollector));
    }

    public override async Task ExecuteOperationAsync(CancellationToken stoppingToken)
    {
        var metrics = await _metricsCollector.CollectMetricsAsync(stoppingToken);
        
        if (metrics.MemoryUsageMb > MemoryThresholdBytes / 1024.0 / 1024.0 ||
            metrics.CpuTimeMs > CpuThresholdMs)
        {
            GC.Collect();
            await _stateManager.UpdateState("Optimizing");
            // Force cleanup
            GC.WaitForPendingFinalizers();
            GC.Collect(2, GCCollectionMode.Aggressive);
            
            var newMetrics = await _metricsCollector.CollectMetricsAsync(stoppingToken);
            await _stateManager.UpdateState("Optimized", _metricsCollector.ConvertToDictionary(newMetrics));
        }
    }
}
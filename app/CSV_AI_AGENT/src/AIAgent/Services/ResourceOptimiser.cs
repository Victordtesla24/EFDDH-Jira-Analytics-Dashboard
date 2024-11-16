// Services/ResourceOptimizer.cs
using System.Diagnostics;
using Microsoft.Extensions.Logging;

namespace AIAgent.Services;

public class ResourceOptimizer
{
    private readonly ILogger<ResourceOptimizer> _logger;
    private readonly Process _currentProcess;

    public ResourceOptimizer(ILogger<ResourceOptimizer> logger)
    {
        _logger = logger;
        _currentProcess = Process.GetCurrentProcess();
    }

    public double GetMemoryUsage()
    {
        return _currentProcess.WorkingSet64 / 1024.0 / 1024.0;
    }

    public bool OptimizeResources()
    {
        var workingSet = _currentProcess.WorkingSet64;
        var privateMemory = _currentProcess.PrivateMemorySize64;
        var mbWorkingSet = workingSet / 1024.0 / 1024.0;
        var mbPrivateMemory = privateMemory / 1024.0 / 1024.0;

        _logger.LogInformation($"Working Set: {mbWorkingSet:F2}MB, Private Memory: {mbPrivateMemory:F2}MB");
        
        if (mbWorkingSet > 400)
        {
            GC.Collect();
            _logger.LogWarning("High memory usage detected - garbage collection triggered");
            return true;
        }
        return false;
    }
}
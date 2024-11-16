// src/AIAgent/Services/BackgroundOperations/BaseBackgroundService.cs
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Threading;
using System.Threading.Tasks;
using AIAgent.Services;

namespace AIAgent.Services.BackgroundOperations;

public abstract class BaseBackgroundService : BackgroundService
{
    protected readonly ILogger _logger;
    private readonly TimeSpan _interval;
    private readonly ErrorHandler _errorHandler;

    protected BaseBackgroundService(
        ILogger logger,
        TimeSpan interval,
        ErrorHandler errorHandler)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _interval = interval;
        _errorHandler = errorHandler ?? throw new ArgumentNullException(nameof(errorHandler));
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ExecuteOperationAsync(stoppingToken);
                await Task.Delay(_interval, stoppingToken);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                _logger.LogError(ex, "Error in {ServiceName}: {Message}", 
                    GetType().Name, ex.Message);
                await _errorHandler.HandleError(ex, $"{GetType().Name} operation failed");
            }
        }
    }

    public abstract Task ExecuteOperationAsync(CancellationToken stoppingToken);
}
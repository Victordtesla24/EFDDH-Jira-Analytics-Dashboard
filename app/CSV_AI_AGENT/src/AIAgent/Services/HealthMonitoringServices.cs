// Services/HealthMonitoringServices.cs
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using AIAgent.Models; // Add this

namespace AIAgent.Services;

public class HealthMonitorService : BackgroundService
{
    private readonly ILogger<HealthMonitorService> _logger;
    private readonly AgentState _state;

    public HealthMonitorService(ILogger<HealthMonitorService> logger)
    {
        _logger = logger;
        _state = new AgentState();
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            _state.LastUpdate = DateTime.UtcNow;
            _logger.LogInformation("Health check at: {time}", _state.LastUpdate);
            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
    }
}
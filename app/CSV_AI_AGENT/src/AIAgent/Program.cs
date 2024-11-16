// Program.cs
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Diagnostics.HealthChecks;
using AIAgent;
using AIAgent.Services;
using AIAgent.Services.BackgroundOperations;

var builder = Host.CreateDefaultBuilder(args);

builder.ConfigureServices(services =>
{
    // Core services
    services.AddSingleton<StateManager>();
    services.AddSingleton<ErrorHandler>();
    services.AddSingleton<IMetricsCollector, MetricsCollector>();
    services.AddSingleton<ResourceOptimizer>();
    
    // File processing
    services.AddSingleton<IFileProcessingService, FileProcessingService>();
    services.AddSingleton<ModelImprovementService>();

    // Background services
    services.AddHostedService<Worker>();
    services.AddHostedService<HealthMonitorService>();
    services.AddHostedService<ModelImprovement>();
    services.AddHostedService<SystemResourceOptimizer>();

    // Health checks
    services.AddHealthChecks()
        .AddCheck("basic_health_check", () => HealthCheckResult.Healthy());

    // Existing services...
    services.AddSingleton<AIAgentInteraction>();
});

var app = builder.Build();
await app.RunAsync();
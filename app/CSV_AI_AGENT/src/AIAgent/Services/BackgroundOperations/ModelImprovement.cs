// src/AIAgent/Services/BackgroundOperations/ModelImprovement.cs
namespace AIAgent.Services.BackgroundOperations;

public class ModelImprovement : BaseBackgroundService
{
    private readonly ModelImprovementService _improvementService;
    private readonly IMetricsCollector _metricsCollector;
    private readonly StateManager _stateManager;
    private readonly IFileProcessingService _fileProcessingService;

    public ModelImprovement(
        ILogger<ModelImprovement> logger,
        ModelImprovementService improvementService,
        IMetricsCollector metricsCollector,
        StateManager stateManager,
        ErrorHandler errorHandler,
        IFileProcessingService fileProcessingService)
        : base(logger, TimeSpan.FromMinutes(5), errorHandler)
    {
        _improvementService = improvementService;
        _metricsCollector = metricsCollector;
        _stateManager = stateManager;
        _fileProcessingService = fileProcessingService;
    }

    public override async Task ExecuteOperationAsync(CancellationToken stoppingToken)
    {
        var dataPath = Path.Combine(Directory.GetCurrentDirectory(), "data");
        if (!Directory.Exists(dataPath))
        {
            Directory.CreateDirectory(dataPath);
        }

        var metrics = await _metricsCollector.CollectMetricsAsync(stoppingToken);
        
        if (!metrics.IsHealthy || metrics.JiraMetrics.GetValueOrDefault("epics_total", 0) == 0)
        {
            _logger.LogWarning("Anomaly detected in JIRA metrics - initiating self-healing");
            await _stateManager.UpdateState("Self-Healing");

            var files = Directory.GetFiles(dataPath, "*.csv");
            if (files.Length == 0)
            {
                _logger.LogWarning("No CSV files found in {path}", dataPath);
                return;
            }

            foreach (var file in files)
            {
                try
                {
                    _logger.LogInformation("Processing file: {file}", file);
                    await _fileProcessingService.ProcessFileAsync(file, stoppingToken);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Error processing file: {file}", file);
                }
            }
        }
    }
}
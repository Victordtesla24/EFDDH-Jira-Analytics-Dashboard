// Worker.cs
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using AIAgent.Services;
using System.IO;

namespace AIAgent;

public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IFileProcessingService _fileProcessingService;
    private readonly StateManager _stateManager;
    private readonly ResourceOptimizer _resourceOptimizer;
    private readonly ModelImprovementService _modelImprover;
    private readonly ErrorHandler _errorHandler;
    private FileSystemWatcher? _watcher;
    private readonly string _watchPath;
    private int _processedFiles;

    public Worker(
        ILogger<Worker> logger,
        IFileProcessingService fileProcessingService,
        StateManager stateManager,
        ResourceOptimizer resourceOptimizer,
        ModelImprovementService modelImprover,
        ErrorHandler errorHandler)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _fileProcessingService = fileProcessingService ?? throw new ArgumentNullException(nameof(fileProcessingService));
        _stateManager = stateManager ?? throw new ArgumentNullException(nameof(stateManager));
        _resourceOptimizer = resourceOptimizer ?? throw new ArgumentNullException(nameof(resourceOptimizer));
        _modelImprover = modelImprover ?? throw new ArgumentNullException(nameof(modelImprover));
        _errorHandler = errorHandler ?? throw new ArgumentNullException(nameof(errorHandler));
        
        _watchPath = Path.Combine(Directory.GetCurrentDirectory(), "data");
        
        // Ensure data directory exists
        if (!Directory.Exists(_watchPath))
        {
            Directory.CreateDirectory(_watchPath);
        }
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("AI Agent starting...");
        _logger.LogInformation($"Watching directory: {_watchPath}");

        SetupFileWatcher();
        
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await _stateManager.UpdateState("Running");
                _resourceOptimizer.OptimizeResources();
                
                if (_processedFiles > 0 && _processedFiles % 10 == 0)
                {
                    await _modelImprover.ImproveModel(_stateManager.GetCurrentState().Metrics);
                }

                await Task.Delay(5000, stoppingToken);
            }
            catch (Exception ex)
            {
                await _errorHandler.HandleError(ex, "Main loop");
            }
        }
    }

    private void SetupFileWatcher()
    {
        _watcher = new FileSystemWatcher(_watchPath, "*.csv")
        {
            NotifyFilter = NotifyFilters.FileName | NotifyFilters.LastWrite,
            EnableRaisingEvents = true
        };

        // Use async event handler
        _watcher.Created += async (sender, e) => 
        {
            try 
            {
                await ProcessNewFile(e.FullPath);
            }
            catch (Exception ex)
            {
                await _errorHandler.HandleError(ex, "File watcher error");
            }
        };

        _watcher.Error += async (sender, e) => await _errorHandler.HandleError(e.GetException(), "File watcher error");
    }

    private async Task ProcessNewFile(string filePath)
    {
        try
        {
            var startTime = DateTime.UtcNow;
            await _stateManager.UpdateState($"Processing: {Path.GetFileName(filePath)}");

            await _fileProcessingService.ProcessFileAsync(filePath);
            _processedFiles++;
            
            var processingTime = (DateTime.UtcNow - startTime).TotalMilliseconds;
            var metrics = new Dictionary<string, double>
            {
                { "total_files_processed", _processedFiles },
                { "processing_time_ms", processingTime },
                { "memory_usage_mb", _resourceOptimizer.GetMemoryUsage() },
                { "last_processed_timestamp", DateTime.UtcNow.Ticks }
            };
            
            await _stateManager.UpdateState("Idle", metrics);
            
            if (_processedFiles % 10 == 0)
            {
                await _modelImprover.ImproveModel(metrics);
            }
        }
        catch (Exception ex)
        {
            await _errorHandler.HandleError(ex, $"Processing file: {filePath}");
            await _stateManager.UpdateState("Error", new Dictionary<string, double> 
            { 
                { "error_count", 1 },
                { "last_error_timestamp", DateTime.UtcNow.Ticks }
            });
        }
    }

    public override void Dispose()
    {
        _watcher?.Dispose();
        base.Dispose();
    }
}
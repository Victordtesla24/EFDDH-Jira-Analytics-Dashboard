using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using AIAgent.Models;
using CsvHelper;
using CsvHelper.Configuration;
using Microsoft.Extensions.Logging;
using AIAgent.Models.Mapping;  // Add this for JiraIssueMap

namespace AIAgent.Services;

public interface IFileProcessingService
{
    Task ProcessFileAsync(string filePath, CancellationToken cancellationToken = default);
}

public class FileProcessingService : IFileProcessingService
{
    private readonly ILogger<FileProcessingService> _logger;
    private readonly StateManager _stateManager;
    private readonly ErrorHandler _errorHandler;
    private readonly AIAgentInteraction _aiAgent;

    private static class MetricKeys
    {
        public const string TotalIssues = "total_issues";
        public const string Epics = "epics";
        public const string HighPriority = "high_priority";
    }

    public FileProcessingService(
        ILogger<FileProcessingService> logger,
        StateManager stateManager,
        ErrorHandler errorHandler,
        AIAgentInteraction aiAgent)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _stateManager = stateManager ?? throw new ArgumentNullException(nameof(stateManager));
        _errorHandler = errorHandler ?? throw new ArgumentNullException(nameof(errorHandler));
        _aiAgent = aiAgent ?? throw new ArgumentNullException(nameof(aiAgent));
    }

    public async Task ProcessFileAsync(string filePath, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(filePath))
            throw new ArgumentException("File path cannot be empty", nameof(filePath));

        if (!File.Exists(filePath))
            throw new FileNotFoundException("CSV file not found", filePath);

        try
        {
            _logger.LogInformation("Processing file: {FileName}", Path.GetFileName(filePath));
            
            var records = await ReadRecordsFromFile<JiraIssue>(filePath, cancellationToken);
            var metrics = CalculateMetrics(records);

            if (metrics["epics_total"] == 0 && records.Any(r => r.IssueType?.Contains("Epic") == true))
            {
                await _aiAgent.ProposeAndAutoFix(
                    "Epic Detection Failed",
                    "Updating CSV mappings to fix Epic detection",
                    async () => {
                        _logger.LogInformation("Applying CSV mapping fix...");
                        records = await ReadRecordsFromFile<JiraIssue>(filePath, cancellationToken);
                        metrics = CalculateMetrics(records);
                    }
                );
            }

            _logger.LogInformation("Processed {Count} records", records.Count);
            await _stateManager.UpdateState("Idle", metrics);
        }
        catch (Exception ex)
        {
            await _aiAgent.ProposeAndAutoFix(
                "JIRA Epic Detection Failed",
                "Update CSV mapping to fix Epic detection",
                async () => 
                {
                    await _stateManager.UpdateState("Fixing");
                    // Auto-fix implementation
                    await _stateManager.UpdateState("Fixed");
                });
            await _errorHandler.HandleError(ex, $"Error processing {filePath}");
            throw;
        }
    }

    private void ValidateFilePath(string filePath)
    {
        if (string.IsNullOrEmpty(filePath))
            throw new ArgumentException("File path cannot be empty", nameof(filePath));

        if (!File.Exists(filePath))
            throw new FileNotFoundException("CSV file not found", filePath);
    }

    private async Task<List<JiraIssue>> ReadRecordsFromFile<T>(string filePath, CancellationToken cancellationToken) where T : class, IJiraItem
    {
        using var reader = new StreamReader(filePath);
        using var csv = CreateCsvReader(reader);

        try
        {
            // Read records asynchronously
            var records = await Task.Run(() => 
            {
                csv.Read();
                csv.ReadHeader();
                var result = new List<JiraIssue>();
                
                while (csv.Read())
                {
                    cancellationToken.ThrowIfCancellationRequested();
                    var record = csv.GetRecord<JiraIssue>();
                    if (record != null)
                    {
                        result.Add(record);
                    }
                }
                return result;
            }, cancellationToken);

            if (records.Any())
            {
                var sample = records.First();
                _logger.LogDebug(@"Sample Record:
                    IssueType: '{IssueType}'
                    Status: '{Status}'
                    Epic: '{Epic}'", 
                    sample.IssueType?.Trim(),
                    sample.Status?.Trim(),
                    sample.Epic?.Trim());
            }

            return records;
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            _logger.LogError(ex, "Error reading CSV file: {FilePath}", filePath);
            throw;
        }
    }

    private static CsvReader CreateCsvReader(TextReader reader)
    {
        var config = new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            HeaderValidated = null,
            MissingFieldFound = null,
            Delimiter = ","
        };
        var csv = new CsvReader(reader, config);
        csv.Context.RegisterClassMap<JiraIssueMap>();  // Register the map
        return csv;
    }

    private static List<T> ProcessRecords<T>(CsvReader csv) where T : class, IJiraItem
    {
        return csv.GetRecords<T>().ToList();
    }

    private Dictionary<string, double> CalculateMetrics(List<JiraIssue> records)
    {
        var epics = records.Where(r => 
            r.IssueType?.Trim().Equals("Epic", StringComparison.OrdinalIgnoreCase) ?? false).ToList();

        _logger.LogInformation("Found {count} Epics", epics.Count);

        return new Dictionary<string, double>
        {
            { "total_issues", records.Count },
            { "epics_total", epics.Count },
            { "arf_epics", epics.Count(e => e.Epic?.StartsWith("ARF223:", StringComparison.OrdinalIgnoreCase) ?? false) },
            { "framework_epics", epics.Count(e => e.Epic?.StartsWith("Framework:", StringComparison.OrdinalIgnoreCase) ?? false) },
            { "metapae_epics", epics.Count(e => e.Epic?.StartsWith("Metapae:", StringComparison.OrdinalIgnoreCase) ?? false) },
            { "epic_in_progress", epics.Count(e => e.Status?.Contains("Progress", StringComparison.OrdinalIgnoreCase) ?? false) },
            { "backlog_items", records.Count(r => r.Status?.Equals("Backlog", StringComparison.OrdinalIgnoreCase) ?? false) },
            { "high_priority", records.Count(r => r.Priority?.Equals("High", StringComparison.OrdinalIgnoreCase) ?? false) }
        };
    }

    private static string GetEpicCategory(string? epic)
    {
        if (string.IsNullOrEmpty(epic)) return "Unknown";
        if (epic.StartsWith("ARF223:", StringComparison.OrdinalIgnoreCase)) return "ARF223";
        if (epic.StartsWith("Framework:", StringComparison.OrdinalIgnoreCase)) return "Framework";
        if (epic.StartsWith("Metapae:", StringComparison.OrdinalIgnoreCase)) return "Metapae";
        if (epic.Equals("Misc", StringComparison.OrdinalIgnoreCase)) return "Misc";
        return "Other";
    }

    private void LogDetailedMetrics(Dictionary<string, double> metrics, 
        Dictionary<string, int> epicsByCategory)
    {
        _logger.LogInformation(@"
JIRA Analysis Summary
--------------------
Total Issues: {TotalIssues}
Epic Breakdownc (Total: {EpicsTotal}):
  - ARF223: {ArfEpics}
  - Framework: {FrameworkEpics}
  - Metapae: {MetapaeEpics}
  - Misc/Other: {MiscEpics}
Status:
  - In Progress: {InProgress}
  - Backlog: {Backlog}
Priorities:
  - High Priority: {HighPriority}
Story Points: {StoryPoints}",
            metrics["total_issues"],
            metrics["epics_total"],
            metrics["arf_epics"],
            metrics["framework_epics"],
            metrics["metapae_epics"],
            metrics["misc_epics"],
            metrics["epic_in_progress"],
            metrics["backlog_items"],
            metrics["high_priority"],
            metrics["story_points_total"]);
    }

    private static bool HasEpicPrefix(string? epic, string prefix) =>
        !string.IsNullOrEmpty(epic) && epic.StartsWith(prefix, StringComparison.OrdinalIgnoreCase);

    private static bool IsStatus(IJiraItem item, string status) =>
        item?.Status?.Trim().Contains(status, StringComparison.OrdinalIgnoreCase) ?? false;

    private static bool IsEpic(IJiraItem item) => 
        item?.IssueType?.Trim().Equals("Epic", StringComparison.OrdinalIgnoreCase) ?? false;

    private static bool IsHighPriority(IJiraItem item) => 
        item?.Priority?.Trim().Equals("High", StringComparison.OrdinalIgnoreCase) ?? false;
}
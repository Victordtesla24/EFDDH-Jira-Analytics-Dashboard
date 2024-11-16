using System;
using System.IO;
using System.Threading.Tasks;
using Xunit;
using Moq;
using AIAgent.Services;
using AIAgent.Models;
using Microsoft.Extensions.Logging;

namespace AIAgent.Tests;

public class FileProcessingServiceTests
{
    private readonly Mock<ILogger<FileProcessingService>> _logger;
    private readonly Mock<StateManager> _stateManager;
    private readonly Mock<ErrorHandler> _errorHandler;
    private readonly FileProcessingService _service;

    public FileProcessingServiceTests()
    {
        _logger = new Mock<ILogger<FileProcessingService>>();
        _stateManager = new Mock<StateManager>(Mock.Of<ILogger<StateManager>>());
        _errorHandler = new Mock<ErrorHandler>(Mock.Of<ILogger<ErrorHandler>>(), _stateManager.Object);
        _service = new FileProcessingService(_logger.Object, _stateManager.Object, _errorHandler.Object);
    }

    [Fact]
    public async Task ProcessFileAsync_ValidJiraData_UpdatesMetrics()
    {
        // Arrange
        var testFile = Path.Combine("TestData", "test.csv");
        Directory.CreateDirectory("TestData");
        File.WriteAllText(testFile, @"IssueKey,IssueType,Priority
EFDDH-1,Epic,High");

        // Act
        await _service.ProcessFileAsync(testFile);

        // Assert
        _stateManager.Verify(x => x.UpdateState(
            It.Is<string>(s => s == "Idle"),
            It.Is<Dictionary<string, double>>(d => 
                d["total_issues"] == 1 && 
                d["epics"] == 1 && 
                d["high_priority"] == 1)
        ));
    }

    [Fact]
    public async Task ProcessFileAsync_EmptyFile_ThrowsException()
    {
        // Arrange
        var testFile = Path.Combine("TestData", "empty.csv");
        Directory.CreateDirectory("TestData");
        File.WriteAllText(testFile, "IssueKey,IssueType,Priority");

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(() => 
            _service.ProcessFileAsync(testFile));
    }

    [Fact]
    public async Task ProcessFileAsync_MultipleRecords_CalculatesMetricsCorrectly()
    {
        // Arrange
        var testFile = Path.Combine("TestData", "multiple.csv");
        Directory.CreateDirectory("TestData");
        File.WriteAllText(testFile, @"IssueKey,IssueType,Priority
EFDDH-1,Epic,High
EFDDH-2,Story,Medium
EFDDH-3,Epic,Low");

        // Act
        await _service.ProcessFileAsync(testFile);

        // Assert
        _stateManager.Verify(x => x.UpdateState(
            It.Is<string>(s => s == "Idle"),
            It.Is<Dictionary<string, double>>(d => 
                d["total_issues"] == 3 && 
                d["epics"] == 2 && 
                d["high_priority"] == 1)
        ));
    }

    [Fact]
    public async Task ProcessFileAsync_EFDDHJiraData_ProcessesCorrectly()
    {
        // Arrange
        var testFile = Path.Combine("TestData", "EFDDH-Jira-Data-Sample.csv");
        Directory.CreateDirectory("TestData");
        File.WriteAllText(testFile, @"Issue key,Issue id,Parent Story,Project key,Project name,Issue Type,Priority,Epic Issue Key,Epic,Summary
EFDDH-1,7117305,N/A,EFDDH,Enterprise Finance,Epic,High,EFDDH-1,Test Epic,Test Summary
EFDDH-2,7117306,,EFDDH,Enterprise Finance,Story,Medium,EFDDH-1,Test Epic,Story Summary");

        // Act
        await _service.ProcessFileAsync(testFile);

        // Assert
        _stateManager.Verify(x => x.UpdateState(
            It.Is<string>(s => s == "Idle"),
            It.Is<Dictionary<string, double>>(d => 
                d["total_issues"] == 2 && 
                d["epics"] == 1 && 
                d["stories"] == 1 && 
                d["high_priority"] == 1)
        ));
    }
}
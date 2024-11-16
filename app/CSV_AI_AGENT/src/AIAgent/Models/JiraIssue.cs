// src/AIAgent/Models/JiraIssue.cs
namespace AIAgent.Models;

public class JiraIssue : IJiraItem
{
    // Required by interface
    public required string IssueKey { get; init; }
    public required string IssueType { get; init; }
    public required string Priority { get; init; }
    
    // Required fields from CSV
    public required string IssueId { get; init; }
    public required string ProjectKey { get; init; }
    public required string ProjectName { get; init; }
    
    // Optional fields matching CSV structure
    public string? ParentStory { get; init; }
    public string? EpicIssueKey { get; init; }
    public string? Epic { get; init; }
    public string? Summary { get; init; }
    public string? AcceptanceCriteria { get; init; }
    public string? StoryPoints { get; init; }
    public string? Assignee { get; init; }
    public string? Status { get; init; }
    public string? Sprint { get; init; }
    public string? DueDate { get; init; }
    public string? Created { get; init; }
}
// JiraIssueMap.cs
// src/AIAgent/Models/Converters/TrimConverter.cs
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.TypeConversion;

namespace AIAgent.Models.Converters;
using CsvHelper.Configuration;

public sealed class JiraIssueMap : ClassMap<JiraIssue>
{
    public JiraIssueMap()
    {
        Map(m => m.IssueKey).Name("Issue key");
        Map(m => m.IssueId).Name("Issue id");
        Map(m => m.ParentStory).Name("Parent Story");
        Map(m => m.ProjectKey).Name("Project key");
        Map(m => m.ProjectName).Name("Project name");
        Map(m => m.IssueType).Name("Issue Type").TypeConverter<TrimConverter>();
        Map(m => m.Priority).Name("Priority");
        Map(m => m.EpicIssueKey).Name("Epic Issue Key");
        Map(m => m.Epic).Name("Epic");
        Map(m => m.Summary).Name("Summary");
        Map(m => m.AcceptanceCriteria).Name("Acceptance Criteria");
        Map(m => m.Status).Name("Status").TypeConverter<TrimConverter>();
        Map(m => m.StoryPoints).Name("Story Points");
    }
}
// TrimConverter.cs
public class TrimConverter : DefaultTypeConverter
{
    public override object? ConvertFromString(string? text, IReaderRow row, MemberMapData memberMapData)
    {
        return text?.Trim();
    }

    public override string? ConvertToString(object? value, IWriterRow row, MemberMapData memberMapData)
    {
        return value?.ToString()?.Trim();
    }
}
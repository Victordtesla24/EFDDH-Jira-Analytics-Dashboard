// src/AIAgent/Models/Converters/TrimConverter.cs
using CsvHelper;
using CsvHelper.Configuration;
using CsvHelper.TypeConversion;

namespace AIAgent.Models.Converters
{
    public class TrimConverter : DefaultTypeConverter
    {
        public override object? ConvertFromString(string? text, IReaderRow row, MemberMapData memberMapData)
        {
            return text?.Trim();
        }
    }
}
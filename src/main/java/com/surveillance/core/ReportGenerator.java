package com.surveillance.core;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Generates surveillance reports in various formats.
 */
public class ReportGenerator {
    
    private String outputDirectory = "reports";

    public ReportGenerator() {
        // Ensure reports directory exists
        new File(outputDirectory).mkdirs();
    }

    public ReportGenerator(String outputDirectory) {
        this.outputDirectory = outputDirectory;
        new File(outputDirectory).mkdirs();
    }

    /**
     * Generate a report from detection results.
     */
    public String generateReport(DetectionResult result, String format, String reportName) {
        String fileName = reportName + "." + format;
        String filePath = outputDirectory + "/" + fileName;

        try {
            switch (format.toLowerCase()) {
                case "csv":
                    generateCsvReport(result, filePath);
                    break;
                case "json":
                    generateJsonReport(result, filePath);
                    break;
                default:
                    generateCsvReport(result, filePath);
            }
            return filePath;
        } catch (IOException e) {
            System.err.println("Error generating report: " + e.getMessage());
            return null;
        }
    }

    private void generateCsvReport(DetectionResult result, String filePath) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            // Header
            writer.println("TradeId,AccountId,Symbol,AlertType,Severity,Description,Timestamp");
            
            // Data rows
            for (DetectionResult.Alert alert : result.getAlerts()) {
                writer.printf("%s,%s,%s,%s,%s,%s,%s%n",
                    nullSafe(alert.getTradeId()),
                    nullSafe(alert.getAccountId()),
                    nullSafe(alert.getSymbol()),
                    nullSafe(alert.getAlertType()),
                    nullSafe(alert.getSeverity()),
                    nullSafe(alert.getDescription()),
                    nullSafe(alert.getTimestamp())
                );
            }
            
            // Summary
            writer.println();
            writer.println("# Summary");
            writer.printf("# Report Type: %s%n", result.getReportType());
            writer.printf("# Total Alerts: %d%n", result.getAlertCount());
            writer.printf("# Execution Time: %d ms%n", result.getExecutionTimeMs());
            writer.printf("# Generated: %s%n", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        }
    }

    private void generateJsonReport(DetectionResult result, String filePath) throws IOException {
        try (PrintWriter writer = new PrintWriter(new FileWriter(filePath))) {
            writer.println("{");
            writer.printf("  \"reportType\": \"%s\",%n", result.getReportType());
            writer.printf("  \"alertCount\": %d,%n", result.getAlertCount());
            writer.printf("  \"executionTimeMs\": %d,%n", result.getExecutionTimeMs());
            writer.println("  \"alerts\": [");
            
            var alerts = result.getAlerts();
            for (int i = 0; i < alerts.size(); i++) {
                var alert = alerts.get(i);
                writer.println("    {");
                writer.printf("      \"tradeId\": \"%s\",%n", nullSafe(alert.getTradeId()));
                writer.printf("      \"accountId\": \"%s\",%n", nullSafe(alert.getAccountId()));
                writer.printf("      \"symbol\": \"%s\",%n", nullSafe(alert.getSymbol()));
                writer.printf("      \"alertType\": \"%s\",%n", nullSafe(alert.getAlertType()));
                writer.printf("      \"severity\": \"%s\",%n", nullSafe(alert.getSeverity()));
                writer.printf("      \"description\": \"%s\"%n", nullSafe(alert.getDescription()));
                writer.print("    }");
                if (i < alerts.size() - 1) writer.print(",");
                writer.println();
            }
            
            writer.println("  ]");
            writer.println("}");
        }
    }

    private String nullSafe(String value) {
        return value != null ? value : "";
    }
}

package com.surveillance.detectors;

import com.surveillance.core.DetectionResult;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * Detector for wash trade patterns.
 * A wash trade occurs when an investor simultaneously sells and buys 
 * the same financial instruments to create misleading, artificial activity.
 */
public class WashTradeDetector {
    
    private String configPath;
    private Date startDate;
    private Date endDate;
    private String accountId;
    private String symbol;
    private int minTradeCount = 5;
    private double priceTolerance = 0.01;
    private int timeWindowSeconds = 300;

    public WashTradeDetector(String configPath) {
        this.configPath = configPath;
    }

    /**
     * Run wash trade detection with configured parameters.
     */
    public DetectionResult detect() {
        long startTime = System.currentTimeMillis();
        DetectionResult result = new DetectionResult("wash_trade");
        
        System.out.println("=== Wash Trade Detection ===");
        System.out.println("Config: " + configPath);
        System.out.println("Date Range: " + formatDate(startDate) + " to " + formatDate(endDate));
        System.out.println("Account Filter: " + (accountId != null ? accountId : "ALL"));
        System.out.println("Symbol Filter: " + (symbol != null ? symbol : "ALL"));
        System.out.println("Min Trade Count: " + minTradeCount);
        System.out.println("Price Tolerance: " + priceTolerance);
        System.out.println("Time Window: " + timeWindowSeconds + " seconds");
        System.out.println();
        
        // Simulate detection - in real implementation, this would query a database
        // and apply wash trade detection algorithms
        
        // Add sample alerts for demonstration
        if (accountId != null && symbol != null) {
            DetectionResult.Alert alert1 = new DetectionResult.Alert(
                "TRD-" + System.currentTimeMillis(),
                accountId,
                symbol,
                "WASH_TRADE"
            );
            alert1.setSeverity("HIGH");
            alert1.setDescription("Potential wash trade detected: matching buy/sell within " + timeWindowSeconds + "s");
            alert1.setTimestamp(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            result.addAlert(alert1);
            
            DetectionResult.Alert alert2 = new DetectionResult.Alert(
                "TRD-" + (System.currentTimeMillis() + 1),
                accountId,
                symbol,
                "WASH_TRADE"
            );
            alert2.setSeverity("MEDIUM");
            alert2.setDescription("Suspicious trading pattern: same account, opposite trades");
            alert2.setTimestamp(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            result.addAlert(alert2);
        }
        
        long executionTime = System.currentTimeMillis() - startTime;
        result.setExecutionTimeMs(executionTime);
        result.setSummary(String.format("Wash trade detection completed. Found %d alerts in %d ms.",
            result.getAlertCount(), executionTime));
        
        System.out.println(result.getSummary());
        
        return result;
    }

    private String formatDate(Date date) {
        if (date == null) return "N/A";
        return new SimpleDateFormat("yyyy-MM-dd").format(date);
    }

    // Setters
    public void setStartDate(Date startDate) { this.startDate = startDate; }
    public void setEndDate(Date endDate) { this.endDate = endDate; }
    public void setAccountId(String accountId) { this.accountId = accountId; }
    public void setSymbol(String symbol) { this.symbol = symbol; }
    public void setMinTradeCount(int minTradeCount) { this.minTradeCount = minTradeCount; }
    public void setPriceTolerance(double priceTolerance) { this.priceTolerance = priceTolerance; }
    public void setTimeWindowSeconds(int timeWindowSeconds) { this.timeWindowSeconds = timeWindowSeconds; }
}

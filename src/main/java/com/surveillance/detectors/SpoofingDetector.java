package com.surveillance.detectors;

import com.surveillance.core.DetectionResult;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * Detector for spoofing and layering patterns.
 * Spoofing involves placing orders with intent to cancel before execution
 * to manipulate prices.
 */
public class SpoofingDetector {
    
    private String configPath;
    private Date startDate;
    private Date endDate;
    private String accountId;
    private String symbol;
    private double cancelRateThreshold = 0.75;
    private int maxOrderLifetimeMs = 500;
    private int minOrderCount = 10;
    private double priceImpactThreshold = 0.02;

    public SpoofingDetector(String configPath) {
        this.configPath = configPath;
    }

    /**
     * Run spoofing detection with configured parameters.
     */
    public DetectionResult detect() {
        long startTime = System.currentTimeMillis();
        DetectionResult result = new DetectionResult("spoofing");
        
        System.out.println("=== Spoofing Detection ===");
        System.out.println("Config: " + configPath);
        System.out.println("Date Range: " + formatDate(startDate) + " to " + formatDate(endDate));
        System.out.println("Account Filter: " + (accountId != null ? accountId : "ALL"));
        System.out.println("Symbol Filter: " + (symbol != null ? symbol : "ALL"));
        System.out.println("Cancel Rate Threshold: " + cancelRateThreshold);
        System.out.println("Max Order Lifetime: " + maxOrderLifetimeMs + " ms");
        System.out.println();
        
        // Simulate detection
        if (accountId != null || symbol != null) {
            DetectionResult.Alert alert = new DetectionResult.Alert(
                "ORD-" + System.currentTimeMillis(),
                accountId,
                symbol,
                "SPOOFING"
            );
            alert.setSeverity("HIGH");
            alert.setDescription("High cancel rate detected: orders cancelled within " + maxOrderLifetimeMs + "ms");
            alert.setTimestamp(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            result.addAlert(alert);
        }
        
        long executionTime = System.currentTimeMillis() - startTime;
        result.setExecutionTimeMs(executionTime);
        result.setSummary(String.format("Spoofing detection completed. Found %d alerts in %d ms.",
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
    public void setCancelRateThreshold(double cancelRateThreshold) { this.cancelRateThreshold = cancelRateThreshold; }
    public void setMaxOrderLifetimeMs(int maxOrderLifetimeMs) { this.maxOrderLifetimeMs = maxOrderLifetimeMs; }
    public void setMinOrderCount(int minOrderCount) { this.minOrderCount = minOrderCount; }
    public void setPriceImpactThreshold(double priceImpactThreshold) { this.priceImpactThreshold = priceImpactThreshold; }
    public void setMinOrderSizeMultiplier(double minOrderSizeMultiplier) { /* additional parameter */ }
}

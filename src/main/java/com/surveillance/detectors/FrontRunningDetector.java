package com.surveillance.detectors;

import com.surveillance.core.DetectionResult;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * Detector for front running patterns.
 * Front running occurs when a broker executes orders on their own account
 * ahead of filling customer orders.
 */
public class FrontRunningDetector {
    
    private String configPath;
    private Date startDate;
    private Date endDate;
    private String accountId;
    private String symbol;
    private String traderId;
    private int preTradeWindowMs = 1000;
    private int postTradeWindowMs = 5000;
    private double minOrderSizeRatio = 0.1;
    private double profitThreshold = 100.0;

    public FrontRunningDetector(String configPath) {
        this.configPath = configPath;
    }

    /**
     * Run front running detection with configured parameters.
     */
    public DetectionResult detect() {
        long startTime = System.currentTimeMillis();
        DetectionResult result = new DetectionResult("front_running");
        
        System.out.println("=== Front Running Detection ===");
        System.out.println("Config: " + configPath);
        System.out.println("Date Range: " + formatDate(startDate) + " to " + formatDate(endDate));
        System.out.println("Account Filter: " + (accountId != null ? accountId : "ALL"));
        System.out.println("Symbol Filter: " + (symbol != null ? symbol : "ALL"));
        System.out.println("Trader Filter: " + (traderId != null ? traderId : "ALL"));
        System.out.println("Pre-Trade Window: " + preTradeWindowMs + " ms");
        System.out.println("Post-Trade Window: " + postTradeWindowMs + " ms");
        System.out.println();
        
        // Simulate detection
        if (traderId != null || accountId != null) {
            DetectionResult.Alert alert = new DetectionResult.Alert(
                "FRT-" + System.currentTimeMillis(),
                accountId,
                symbol,
                "FRONT_RUNNING"
            );
            alert.setSeverity("CRITICAL");
            alert.setDescription("Potential front running: proprietary trade executed before customer order");
            alert.setTimestamp(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
            result.addAlert(alert);
        }
        
        long executionTime = System.currentTimeMillis() - startTime;
        result.setExecutionTimeMs(executionTime);
        result.setSummary(String.format("Front running detection completed. Found %d alerts in %d ms.",
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
    public void setTraderId(String traderId) { this.traderId = traderId; }
    public void setPreTradeWindowMs(int preTradeWindowMs) { this.preTradeWindowMs = preTradeWindowMs; }
    public void setPostTradeWindowMs(int postTradeWindowMs) { this.postTradeWindowMs = postTradeWindowMs; }
    public void setMinOrderSizeRatio(double minOrderSizeRatio) { this.minOrderSizeRatio = minOrderSizeRatio; }
    public void setProfitThreshold(double profitThreshold) { this.profitThreshold = profitThreshold; }
    public void setEmployeeId(String employeeId) { this.traderId = employeeId; }
    public void setDepartment(String department) { /* department filter */ }
    public void setTimeWindowBeforeSeconds(int seconds) { this.preTradeWindowMs = seconds * 1000; }
    public void setMinLargeOrderQty(int minLargeOrderQty) { /* min order quantity */ }
    public void setMinPriceMovePct(double minPriceMovePct) { /* price move threshold */ }
}

package com.surveillance.tests;

import org.junit.Test;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * Wash Trade Detection Test
 * 
 * @Meta(component = "wash_trade_test")
 * @Meta(capability = "detect_wash_trades")
 * @Meta(domain = "trade_surveillance")
 * @Meta(report_type = "wash_trade")
 * @Meta(config_file = "wash_trade_detection.yml")
 */
@RunWith(Parameterized.class)
public class WashTradeDetectionTest {

    // Test parameters - can be modified by the agent
    @Parameter("startDate")
    private String startDate = "2024-01-01";
    
    @Parameter("endDate")
    private String endDate = "2024-12-31";
    
    @Parameter("accountId")
    private String accountId = null;
    
    @Parameter("symbol")
    private String symbol = null;
    
    @Parameter("minTradeCount")
    private int minTradeCount = 5;
    
    @Parameter("priceTolerance")
    private double priceTolerance = 0.01;
    
    @Parameter("timeWindowSeconds")
    private int timeWindowSeconds = 300;
    
    @Parameter("outputFormat")
    private String outputFormat = "csv";

    private WashTradeDetector detector;
    private ReportGenerator reportGenerator;
    private String configPath = "configs/wash_trade_detection.yml";

    @Before
    public void setUp() {
        detector = new WashTradeDetector(configPath);
        reportGenerator = new ReportGenerator();
        
        // Configure detector with parameters
        detector.setStartDate(parseDate(startDate));
        detector.setEndDate(parseDate(endDate));
        detector.setAccountId(accountId);
        detector.setSymbol(symbol);
        detector.setMinTradeCount(minTradeCount);
        detector.setPriceTolerance(priceTolerance);
        detector.setTimeWindowSeconds(timeWindowSeconds);
    }

    @Test
    public void testDetectWashTrades() {
        // Run detection
        DetectionResult result = detector.detect();
        
        // Generate report
        String reportPath = reportGenerator.generateReport(
            result, 
            outputFormat,
            "wash_trade_report_" + getCurrentTimestamp()
        );
        
        System.out.println("Report generated: " + reportPath);
        System.out.println("Alerts found: " + result.getAlertCount());
        
        // Assert no critical issues
        assert result != null : "Detection result should not be null";
    }

    @Test
    public void testDetectWashTradesForAccount() {
        // Set specific account for targeted detection
        if (accountId != null) {
            detector.setAccountId(accountId);
        }
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "wash_trade_account_" + accountId + "_" + getCurrentTimestamp()
        );
        
        System.out.println("Account-specific report generated: " + reportPath);
    }

    @Test
    public void testDetectWashTradesForSymbol() {
        // Set specific symbol for targeted detection
        if (symbol != null) {
            detector.setSymbol(symbol);
        }
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "wash_trade_symbol_" + symbol + "_" + getCurrentTimestamp()
        );
        
        System.out.println("Symbol-specific report generated: " + reportPath);
    }

    private Date parseDate(String dateStr) {
        try {
            return new SimpleDateFormat("yyyy-MM-dd").parse(dateStr);
        } catch (Exception e) {
            return new Date();
        }
    }

    private String getCurrentTimestamp() {
        return new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
    }
}

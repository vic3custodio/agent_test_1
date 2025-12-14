package com.surveillance.tests;

import org.junit.Test;
import org.junit.Before;
import java.util.Date;
import java.text.SimpleDateFormat;

import com.surveillance.core.Parameter;
import com.surveillance.core.DetectionResult;
import com.surveillance.core.ReportGenerator;
import com.surveillance.detectors.SpoofingDetector;

/**
 * Spoofing Detection Test
 * 
 * @Meta(component = "spoofing_test")
 * @Meta(capability = "detect_spoofing")
 * @Meta(domain = "trade_surveillance")
 * @Meta(report_type = "spoofing")
 * @Meta(config_file = "spoofing_detection.yml")
 */
public class SpoofingDetectionTest {

    // Test parameters - can be modified by the agent
    @Parameter("startDate")
    private String startDate = "2024-01-01";
    
    @Parameter("endDate")
    private String endDate = "2024-12-31";
    
    @Parameter("accountId")
    private String accountId = null;
    
    @Parameter("symbol")
    private String symbol = null;
    
    @Parameter("cancelRateThreshold")
    private double cancelRateThreshold = 0.75;
    
    @Parameter("maxOrderLifetimeMs")
    private int maxOrderLifetimeMs = 500;
    
    @Parameter("minOrderSizeMultiplier")
    private double minOrderSizeMultiplier = 5.0;
    
    @Parameter("outputFormat")
    private String outputFormat = "csv";

    private SpoofingDetector detector;
    private ReportGenerator reportGenerator;
    private String configPath = "configs/spoofing_detection.yml";

    @Before
    public void setUp() {
        detector = new SpoofingDetector(configPath);
        reportGenerator = new ReportGenerator();
        
        // Configure detector with parameters
        detector.setStartDate(parseDate(startDate));
        detector.setEndDate(parseDate(endDate));
        detector.setAccountId(accountId);
        detector.setSymbol(symbol);
        detector.setCancelRateThreshold(cancelRateThreshold);
        detector.setMaxOrderLifetimeMs(maxOrderLifetimeMs);
        detector.setMinOrderSizeMultiplier(minOrderSizeMultiplier);
    }

    @Test
    public void testDetectSpoofing() {
        // Run detection
        DetectionResult result = detector.detect();
        
        // Generate report
        String reportPath = reportGenerator.generateReport(
            result, 
            outputFormat,
            "spoofing_report_" + getCurrentTimestamp()
        );
        
        System.out.println("Report generated: " + reportPath);
        System.out.println("Alerts found: " + result.getAlertCount());
        
        // Assert no critical issues
        assert result != null : "Detection result should not be null";
    }

    @Test
    public void testDetectLayering() {
        // Layering detection with stricter thresholds
        detector.setCancelRateThreshold(0.90);
        detector.setMaxOrderLifetimeMs(200);
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "layering_report_" + getCurrentTimestamp()
        );
        
        System.out.println("Layering report generated: " + reportPath);
    }

    @Test
    public void testDetectSpoofingForAccount() {
        if (accountId != null) {
            detector.setAccountId(accountId);
        }
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "spoofing_account_" + accountId + "_" + getCurrentTimestamp()
        );
        
        System.out.println("Account-specific spoofing report generated: " + reportPath);
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

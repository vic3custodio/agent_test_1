package com.surveillance.tests;

import org.junit.Test;
import org.junit.Before;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import java.util.Date;
import java.text.SimpleDateFormat;

/**
 * Front Running Detection Test
 * 
 * @Meta(component = "front_running_test")
 * @Meta(capability = "detect_front_running")
 * @Meta(domain = "trade_surveillance")
 * @Meta(report_type = "front_running")
 * @Meta(config_file = "front_running_detection.yml")
 */
@RunWith(Parameterized.class)
public class FrontRunningDetectionTest {

    // Test parameters - can be modified by the agent
    @Parameter("startDate")
    private String startDate = "2024-01-01";
    
    @Parameter("endDate")
    private String endDate = "2024-12-31";
    
    @Parameter("employeeId")
    private String employeeId = null;
    
    @Parameter("department")
    private String department = null;
    
    @Parameter("symbol")
    private String symbol = null;
    
    @Parameter("timeWindowBeforeSeconds")
    private int timeWindowBeforeSeconds = 300;
    
    @Parameter("minLargeOrderQty")
    private int minLargeOrderQty = 10000;
    
    @Parameter("minPriceMovePct")
    private double minPriceMovePct = 0.02;
    
    @Parameter("outputFormat")
    private String outputFormat = "csv";

    private FrontRunningDetector detector;
    private ReportGenerator reportGenerator;
    private String configPath = "configs/front_running_detection.yml";

    @Before
    public void setUp() {
        detector = new FrontRunningDetector(configPath);
        reportGenerator = new ReportGenerator();
        
        // Configure detector with parameters
        detector.setStartDate(parseDate(startDate));
        detector.setEndDate(parseDate(endDate));
        detector.setEmployeeId(employeeId);
        detector.setDepartment(department);
        detector.setSymbol(symbol);
        detector.setTimeWindowBeforeSeconds(timeWindowBeforeSeconds);
        detector.setMinLargeOrderQty(minLargeOrderQty);
        detector.setMinPriceMovePct(minPriceMovePct);
    }

    @Test
    public void testDetectFrontRunning() {
        // Run detection
        DetectionResult result = detector.detect();
        
        // Generate report
        String reportPath = reportGenerator.generateReport(
            result, 
            outputFormat,
            "front_running_report_" + getCurrentTimestamp()
        );
        
        System.out.println("Report generated: " + reportPath);
        System.out.println("Alerts found: " + result.getAlertCount());
        
        // Assert no critical issues
        assert result != null : "Detection result should not be null";
    }

    @Test
    public void testDetectFrontRunningByDepartment() {
        if (department != null) {
            detector.setDepartment(department);
        }
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "front_running_dept_" + department + "_" + getCurrentTimestamp()
        );
        
        System.out.println("Department-specific report generated: " + reportPath);
    }

    @Test
    public void testDetectFrontRunningByEmployee() {
        if (employeeId != null) {
            detector.setEmployeeId(employeeId);
        }
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "front_running_employee_" + employeeId + "_" + getCurrentTimestamp()
        );
        
        System.out.println("Employee-specific report generated: " + reportPath);
    }

    @Test
    public void testDetectInsiderTrading() {
        // Insider trading detection uses similar patterns
        detector.setTimeWindowBeforeSeconds(86400); // 24 hours
        detector.setMinPriceMovePct(0.05); // 5% price move
        
        DetectionResult result = detector.detect();
        
        String reportPath = reportGenerator.generateReport(
            result,
            outputFormat,
            "insider_trading_report_" + getCurrentTimestamp()
        );
        
        System.out.println("Insider trading report generated: " + reportPath);
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

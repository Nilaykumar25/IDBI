# Quick Integration Test Script
Write-Host ""
Write-Host "=== MSME Financial Health Score - Integration Testing ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health Check
Write-Host "Test 1: Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET -UseBasicParsing
Write-Host "OK Backend is healthy - Mode: $($health.mode), Adapter: $($health.adapterMode)" -ForegroundColor Green

# Test 2: Score Computation - Low Risk Profile
Write-Host ""
Write-Host "Test 2: Score Computation (DEMO-LOW-001)..." -ForegroundColor Yellow
$payload = @{
    msmeId = "DEMO-LOW-001"
    gstNumber = "GST-DEMO-LOW-001"
    upiId = "upi-demo-low-001@bank"
    aaConsentToken = "AA-DEMO-LOW-001"
    epfoEstablishmentId = "EPFO-DEMO-LOW-001"
    sector = "Trader"
} | ConvertTo-Json

$score1 = Invoke-RestMethod -Uri "http://localhost:5000/api/scores" -Method POST -Body $payload -ContentType "application/json" -UseBasicParsing
if ($score1.success) {
    Write-Host "OK Score: $([math]::Round($score1.data.compositeScore, 2)), Risk: $($score1.data.riskBand)" -ForegroundColor Green
}

# Test 3: Score Computation - High Risk Profile
Write-Host ""
Write-Host "Test 3: Score Computation (DEMO-HIGH-001)..." -ForegroundColor Yellow
$payload2 = @{
    msmeId = "DEMO-HIGH-001"
    gstNumber = "GST-DEMO-HIGH-001"
    upiId = "upi-demo-high-001@bank"
    aaConsentToken = "AA-DEMO-HIGH-001"
    epfoEstablishmentId = "EPFO-DEMO-HIGH-001"
    sector = "Services"
} | ConvertTo-Json

$score2 = Invoke-RestMethod -Uri "http://localhost:5000/api/scores" -Method POST -Body $payload2 -ContentType "application/json" -UseBasicParsing
if ($score2.success) {
    Write-Host "OK Score: $([math]::Round($score2.data.compositeScore, 2)), Risk: $($score2.data.riskBand)" -ForegroundColor Green
}

# Test 4: Score Computation - Medium Risk Profile
Write-Host ""
Write-Host "Test 4: Score Computation (DEMO-MED-001)..." -ForegroundColor Yellow
$payload3 = @{
    msmeId = "DEMO-MED-001"
    gstNumber = "GST-DEMO-MED-001"
    upiId = "upi-demo-med-001@bank"
    aaConsentToken = "AA-DEMO-MED-001"
    epfoEstablishmentId = "EPFO-DEMO-MED-001"
    sector = "Manufacturer"
} | ConvertTo-Json

$score3 = Invoke-RestMethod -Uri "http://localhost:5000/api/scores" -Method POST -Body $payload3 -ContentType "application/json" -UseBasicParsing
if ($score3.success) {
    Write-Host "OK Score: $([math]::Round($score3.data.compositeScore, 2)), Risk: $($score3.data.riskBand)" -ForegroundColor Green
}

# Test 5: Score Computation - Partial Data Profile
Write-Host ""
Write-Host "Test 5: Score Computation with Partial Data (DEMO-PARTIAL-001)..." -ForegroundColor Yellow
$payload4 = @{
    msmeId = "DEMO-PARTIAL-001"
    gstNumber = "GST-DEMO-PARTIAL-001"
    upiId = "upi-demo-partial-001@bank"
    aaConsentToken = "AA-DEMO-PARTIAL-001"
    epfoEstablishmentId = "EPFO-DEMO-PARTIAL-001"
    sector = "Trader"
} | ConvertTo-Json

$score4 = Invoke-RestMethod -Uri "http://localhost:5000/api/scores" -Method POST -Body $payload4 -ContentType "application/json" -UseBasicParsing
if ($score4.success) {
    $missing = if ($score4.data.missingSources) { $score4.data.missingSources -join ", " } else { "None" }
    Write-Host "OK Score: $([math]::Round($score4.data.compositeScore, 2)), Risk: $($score4.data.riskBand), Missing: $missing" -ForegroundColor Green
}

# Test 6: Score Retrieval
Write-Host ""
Write-Host "Test 6: Score Retrieval..." -ForegroundColor Yellow
$retrieved = Invoke-RestMethod -Uri "http://localhost:5000/api/scores/DEMO-LOW-001" -Method GET -UseBasicParsing
if ($retrieved.success) {
    Write-Host "OK Retrieved score for DEMO-LOW-001: $([math]::Round($retrieved.data.compositeScore, 2))" -ForegroundColor Green
}

# Test 7: Score History
Write-Host ""
Write-Host "Test 7: Score History..." -ForegroundColor Yellow
$endDate = Get-Date -Format "yyyy-MM-dd"
$startDate = (Get-Date).AddDays(-180).ToString("yyyy-MM-dd")
$history = Invoke-RestMethod -Uri "http://localhost:5000/api/scores/DEMO-LOW-001/history?startDate=$startDate&endDate=$endDate" -Method GET -UseBasicParsing
if ($history.success) {
    Write-Host "OK Retrieved $($history.data.Count) historical records" -ForegroundColor Green
}

# Test 8: What-If Simulator
Write-Host ""
Write-Host "Test 8: What-If Simulator..." -ForegroundColor Yellow
$simPayload = @{
    features = @{
        revenueStability = 0.95
        transactionVelocity = 0.80
        liquidityRatio = 0.85
        employmentConsistency = 0.75
        complianceScore = 0.90
        growthIndicator = 0.70
    }
    sector = "Trader"
} | ConvertTo-Json

$simResult = Invoke-RestMethod -Uri "http://localhost:5000/api/simulate" -Method POST -Body $simPayload -ContentType "application/json" -UseBasicParsing
if ($simResult.success) {
    Write-Host "OK Simulated Score: $([math]::Round($simResult.data.simulatedScore, 2)), Risk: $($simResult.data.simulatedRiskBand)" -ForegroundColor Green
}

# Test 9: Ecosystem - AA Consent
Write-Host ""
Write-Host "Test 9: Ecosystem - AA Consent..." -ForegroundColor Yellow
$consentPayload = @{ msmeId = "DEMO-LOW-001" } | ConvertTo-Json
$consent = Invoke-RestMethod -Uri "http://localhost:5000/api/ecosystem/consent" -Method POST -Body $consentPayload -ContentType "application/json" -UseBasicParsing
if ($consent.success) {
    Write-Host "OK Consent approved: $($consent.data.consentToken.Substring(0, 20))..." -ForegroundColor Green
}

# Test 10: Ecosystem - ULI Publish
Write-Host ""
Write-Host "Test 10: Ecosystem - ULI Publish..." -ForegroundColor Yellow
$publishPayload = @{
    msmeId = "DEMO-LOW-001"
    score = 85.5
    riskBand = "Low"
} | ConvertTo-Json
$publish = Invoke-RestMethod -Uri "http://localhost:5000/api/ecosystem/publish" -Method POST -Body $publishPayload -ContentType "application/json" -UseBasicParsing
if ($publish.success) {
    Write-Host "OK Published to ULI: $($publish.data.transactionId)" -ForegroundColor Green
}

# Test 11: Ecosystem - Lender Matching
Write-Host ""
Write-Host "Test 11: Ecosystem - Lender Matching (All Risk Bands)..." -ForegroundColor Yellow
$lendersLow = Invoke-RestMethod -Uri "http://localhost:5000/api/ecosystem/lenders?riskBand=Low" -Method GET -UseBasicParsing
if ($lendersLow.success) {
    Write-Host "  OK Low Risk: $($lendersLow.data.Count) lenders matched" -ForegroundColor Green
}
$lendersMed = Invoke-RestMethod -Uri "http://localhost:5000/api/ecosystem/lenders?riskBand=Medium" -Method GET -UseBasicParsing
if ($lendersMed.success) {
    Write-Host "  OK Medium Risk: $($lendersMed.data.Count) lenders matched" -ForegroundColor Green
}
$lendersHigh = Invoke-RestMethod -Uri "http://localhost:5000/api/ecosystem/lenders?riskBand=High" -Method GET -UseBasicParsing
if ($lendersHigh.success) {
    Write-Host "  OK High Risk: $($lendersHigh.data.Count) lenders matched" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== All Backend Tests Complete ===" -ForegroundColor Cyan
Write-Host ""

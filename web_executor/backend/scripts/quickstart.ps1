# ============================================
# RAG Chatbot - Quick Start Script
# ============================================

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🚀 RAG CHATBOT QUICK START" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

$BASE_DIR = "c:\uel\Đồ án tốt nghiệp\finance_portfolio\web_executor"
$BACKEND_DIR = Join-Path $BASE_DIR "backend"
$FRONTEND_DIR = Join-Path $BASE_DIR "frontend"

# ============================================
# Step 1: Check Python
# ============================================
Write-Host "📋 Step 1: Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# ============================================
# Step 2: Install Backend Dependencies
# ============================================
Write-Host ""
Write-Host "📦 Step 2: Installing backend dependencies..." -ForegroundColor Yellow
Set-Location $BACKEND_DIR

if (Test-Path "requirements.txt") {
    Write-Host "Installing from requirements.txt..."
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# ============================================
# Step 3: Prepare RAG Data
# ============================================
Write-Host ""
Write-Host "📊 Step 3: Preparing RAG data..." -ForegroundColor Yellow

$ragDataDir = Join-Path $BACKEND_DIR "data\rag"
if (-not (Test-Path $ragDataDir)) {
    New-Item -ItemType Directory -Path $ragDataDir -Force | Out-Null
    Write-Host "Created data/rag directory" -ForegroundColor Gray
}

$ragSourceDir = "c:\uel\Đồ án tốt nghiệp\rag_system\data\embeddings\ver_06\rag_outputs"
if (Test-Path $ragSourceDir) {
    Write-Host "Found RAG source data at: $ragSourceDir"
    Write-Host "Running data preparation script..."
    
    python scripts\prepare_rag_data.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ RAG data prepared successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Data preparation had warnings (check logs)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  RAG source directory not found: $ragSourceDir" -ForegroundColor Yellow
    Write-Host "   You'll need to manually prepare RAG data" -ForegroundColor Yellow
}

# ============================================
# Step 4: Check .env Configuration
# ============================================
Write-Host ""
Write-Host "⚙️  Step 4: Checking environment configuration..." -ForegroundColor Yellow

$envFile = Join-Path $BACKEND_DIR ".env"
if (Test-Path $envFile) {
    Write-Host "✅ .env file found" -ForegroundColor Green
    
    # Check for required RAG settings
    $envContent = Get-Content $envFile -Raw
    $requiredSettings = @(
        "RAG_ENABLED",
        "RAG_FAISS_INDEX_PATH",
        "RAG_METADATA_PATH"
    )
    
    $missing = @()
    foreach ($setting in $requiredSettings) {
        if ($envContent -notmatch $setting) {
            $missing += $setting
        }
    }
    
    if ($missing.Count -eq 0) {
        Write-Host "✅ All required RAG settings present" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Missing settings in .env:" -ForegroundColor Yellow
        $missing | ForEach-Object { Write-Host "   - $_" -ForegroundColor Gray }
        Write-Host "   Please check .env.example for reference" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Yellow
    Write-Host "   Copying from .env.example..." -ForegroundColor Yellow
    
    $envExample = Join-Path $BACKEND_DIR ".env.example"
    if (Test-Path $envExample) {
        Copy-Item $envExample $envFile
        Write-Host "✅ Created .env from .env.example" -ForegroundColor Green
        Write-Host "   ⚠️  Please edit .env and add your credentials!" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found!" -ForegroundColor Red
    }
}

# ============================================
# Step 5: Test Backend
# ============================================
Write-Host ""
Write-Host "🧪 Step 5: Testing backend setup..." -ForegroundColor Yellow

Write-Host "Testing imports..."
$testScript = @"
try:
    import faiss
    import sentence_transformers
    import google.generativeai
    print('✅ All RAG dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    exit(1)
"@

$testScript | python
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend dependencies working" -ForegroundColor Green
} else {
    Write-Host "❌ Import test failed" -ForegroundColor Red
    exit 1
}

# ============================================
# Step 6: Check Frontend
# ============================================
Write-Host ""
Write-Host "🎨 Step 6: Checking frontend..." -ForegroundColor Yellow
Set-Location $FRONTEND_DIR

if (Test-Path "package.json") {
    Write-Host "✅ Frontend directory found" -ForegroundColor Green
    
    # Check if node_modules exists
    if (-not (Test-Path "node_modules")) {
        Write-Host "⚠️  node_modules not found. Run 'pnpm install' in frontend directory" -ForegroundColor Yellow
    } else {
        Write-Host "✅ node_modules found" -ForegroundColor Green
    }
} else {
    Write-Host "❌ package.json not found in frontend!" -ForegroundColor Red
}

# ============================================
# Summary
# ============================================
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "✨ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Start Backend:" -ForegroundColor White
Write-Host "   cd '$BACKEND_DIR'" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣  Start Frontend (in another terminal):" -ForegroundColor White
Write-Host "   cd '$FRONTEND_DIR'" -ForegroundColor Gray
Write-Host "   pnpm dev" -ForegroundColor Gray
Write-Host ""
Write-Host "3️⃣  Get Gemini API Key:" -ForegroundColor White
Write-Host "   Visit: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
Write-Host ""
Write-Host "4️⃣  Access Chatbot:" -ForegroundColor White
Write-Host "   http://localhost:5173/chat" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - Setup Guide: $BACKEND_DIR\docs\RAG_CHATBOT_SETUP.md" -ForegroundColor Gray
Write-Host "   - Implementation: finance_portfolio\docs\devjourney\03_rag_chatbot_implementation.md" -ForegroundColor Gray
Write-Host ""
Write-Host "🆘 Need help?" -ForegroundColor Yellow
Write-Host "   Check the troubleshooting section in RAG_CHATBOT_SETUP.md" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan

# ============================================
# Prompt to start services
# ============================================
Write-Host ""
$response = Read-Host "Do you want to start the backend now? (Y/n)"
if ($response -eq "" -or $response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "🚀 Starting backend server..." -ForegroundColor Green
    Write-Host "   Press Ctrl+C to stop" -ForegroundColor Gray
    Write-Host ""
    Set-Location $BACKEND_DIR
    python main.py
} else {
    Write-Host ""
    Write-Host "👋 Setup complete! Start services manually when ready." -ForegroundColor Cyan
}

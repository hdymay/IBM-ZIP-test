# C to Java 프로젝트 전용 패키지 수집 스크립트 (Windows)
# 회사 Airflow 서버에 추가로 필요한 패키지만 다운로드

Write-Host "==========================================" -ForegroundColor Green
Write-Host "C to Java 프로젝트 패키지 수집" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "이 스크립트는 회사 Airflow 서버에 추가로 필요한" -ForegroundColor Yellow
Write-Host "C to Java 프로젝트 전용 패키지만 다운로드합니다." -ForegroundColor Yellow
Write-Host ""
Write-Host "회사 Airflow에 이미 설치된 패키지는 제외됩니다:" -ForegroundColor Cyan
Write-Host "  - Flask (Airflow UI용)" -ForegroundColor Cyan
Write-Host "  - SQLAlchemy (Airflow 메타데이터용)" -ForegroundColor Cyan
Write-Host "  - Jinja2, Pendulum 등 Airflow 기본 패키지" -ForegroundColor Cyan
Write-Host ""

# 출력 디렉토리 생성
$OUTPUT_DIR = "c_to_java_wheels"
New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null

# Python 버전 확인
$PYTHON_VERSION = python --version 2>&1 | Select-String -Pattern "\d+\.\d+" | ForEach-Object { $_.Matches.Value }
Write-Host "Python 버전: $PYTHON_VERSION" -ForegroundColor Cyan
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "C to Java 프로젝트 전용 패키지 다운로드" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# C to Java 프로젝트에서 사용하는 패키지 (Airflow 기본 패키지 제외)
$packages = @(
    "requests",        # watsonx.ai API, GitHub API 호출
    "python-dotenv"    # 환경 변수 관리 (.env 파일)
)

foreach ($package in $packages) {
    Write-Host "  다운로드 중: $package" -ForegroundColor Yellow
    pip download `
        --dest $OUTPUT_DIR `
        --python-version $PYTHON_VERSION `
        --platform win_amd64 `
        --only-binary=:all: `
        $package 2>&1 | Out-Null
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "완료!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

$file_count = (Get-ChildItem $OUTPUT_DIR).Count
$total_size = (Get-ChildItem $OUTPUT_DIR | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "다운로드된 패키지 위치: $OUTPUT_DIR" -ForegroundColor Cyan
Write-Host "파일 개수: $file_count" -ForegroundColor Cyan
Write-Host "총 크기: $([math]::Round($total_size, 2)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "다운로드된 패키지:" -ForegroundColor Yellow
Get-ChildItem $OUTPUT_DIR | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
Write-Host ""
Write-Host "회사 Airflow 서버에서 설치 방법:" -ForegroundColor Yellow
Write-Host "  pip install --no-index --find-links=$OUTPUT_DIR requests python-dotenv" -ForegroundColor White
Write-Host ""
Write-Host "USB로 전송:" -ForegroundColor Yellow
Write-Host "  Compress-Archive -Path $OUTPUT_DIR -DestinationPath c_to_java_wheels.zip" -ForegroundColor White

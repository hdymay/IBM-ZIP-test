"""
C to Java 변환 파이프라인 테스트 시스템 메인 모듈

이 모듈은 전체 워크플로우를 조율하는 메인 진입점입니다.
Requirements: 1.1, 7.1, 2.1, 3.1
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config.config_manager import ConfigManager
from src.core.file_selector import FileSelector
from src.core.zip_builder import ZIPBuilder
from src.core.watsonx_uploader import WatsonxUploader
from src.core.github_uploader import GitHubUploader
from src.core.sample_executor import SampleExecutor
from src.models.data_models import Configuration


class PipelineWorkflow:
    """파이프라인 워크플로우 관리 클래스
    
    전체 워크플로우를 조율하고 실행합니다.
    Requirements: 1.1, 2.1, 3.1
    """
    
    def __init__(self):
        """워크플로우 초기화"""
        self.config_manager = ConfigManager()
        self.file_selector = FileSelector()
        self.sample_executor = SampleExecutor()
        self.config = None
        self.zip_builder = None
        self.uploader = None
    
    def run(self):
        """메인 워크플로우 실행
        
        Requirements: 1.1, 7.1
        """
        print("=" * 60)
        print("C to Java 변환 파이프라인 테스트 시스템")
        print("=" * 60)
        print()
        
        try:
            # 1. 설정 로드
            self._load_configuration()
            
            # 2. 파일 선택
            selected_files = self._select_files()
            
            if not selected_files:
                print("선택된 파일이 없습니다. 프로그램을 종료합니다.")
                return
            
            # 3. ZIP 생성
            archive_info = self._create_zip_archive(selected_files)
            
            if not archive_info:
                print("ZIP 생성에 실패했습니다. 프로그램을 종료합니다.")
                return
            
            # 4. watsonx.ai 업로드
            upload_result = self._upload_to_watsonx(archive_info.archive_path)
            
            if not upload_result or not upload_result.success:
                print("watsonx.ai 업로드에 실패했습니다.")
                # GitHub 업로드가 활성화되어 있으면 시도
                if self.config.github_upload_enabled:
                    print("GitHub 업로드를 시도합니다...")
                    github_result = self._upload_to_github(archive_info.archive_path)
                    if github_result and github_result.success:
                        self._display_github_completion(github_result)
                        return
                print("모든 업로드 방법이 실패했습니다.")
                return
            
            # 5. GitHub 업로드 (선택적)
            if self.config.github_upload_enabled:
                print("\n추가로 GitHub에도 업로드합니다...")
                github_result = self._upload_to_github(archive_info.archive_path)
                if github_result and github_result.success:
                    print("✓ GitHub 업로드도 완료되었습니다")
            
            # 6. 완료 메시지
            self._display_completion(upload_result)
            
        except KeyboardInterrupt:
            print("\n\n사용자에 의해 중단되었습니다.")
            sys.exit(0)
        except Exception as e:
            print(f"\n예상치 못한 오류 발생: {str(e)}")
            sys.exit(1)
    
    def _load_configuration(self):
        """설정 로드 및 검증
        
        Requirements: 7.1
        """
        print("📋 설정 로드 중...")
        
        try:
            self.config = self.config_manager.load_config()
            print("✓ 설정 로드 완료")
            
            # 설정 검증
            self.config_manager.validate_config(self.config)
            print("✓ 설정 검증 완료")
            
            # ZIP 빌더 초기화
            self.zip_builder = ZIPBuilder(self.config.output_directory)
            
        except FileNotFoundError:
            print("\n⚠ 설정 파일이 없습니다.")
            print("환경 변수를 설정하거나 설정 파일을 생성하세요.")
            print("\n필요한 환경 변수:")
            print("  - WATSONX_API_KEY")
            print("  - WATSONX_ENDPOINT")
            print("  - WATSONX_PROJECT_ID")
            print("  - OUTPUT_DIRECTORY (선택적, 기본값: ./output)")
            sys.exit(1)
        except ValueError as e:
            print(f"\n❌ 설정 오류: {str(e)}")
            sys.exit(1)
    
    def _select_files(self):
        """파일 선택 인터페이스
        
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        print("\n" + "=" * 60)
        print("파일 선택")
        print("=" * 60)
        
        while True:
            print("\n옵션을 선택하세요:")
            print("  1. 샘플 모드 (samples 디렉토리의 모든 파일)")
            print("  2. 디렉토리 지정")
            print("  3. 종료")
            
            choice = input("\n선택 (1-3): ").strip()
            
            if choice == "1":
                return self._select_sample_mode()
            elif choice == "2":
                return self._select_from_directory()
            elif choice == "3":
                print("프로그램을 종료합니다.")
                sys.exit(0)
            else:
                print("잘못된 선택입니다. 다시 시도하세요.")
    
    def _select_sample_mode(self):
        """샘플 모드 선택
        
        Requirements: 5.3
        """
        print("\n📁 샘플 모드 활성화...")
        
        try:
            selected_files = self.file_selector.select_sample_mode("samples")
            print(f"✓ {len(selected_files)}개의 샘플 파일이 선택되었습니다:")
            
            for file_path in selected_files:
                print(f"  - {Path(file_path).name}")
            
            # 샘플 파일 실행 및 결과 추적
            print("\n🔄 샘플 파일 실행 중...")
            self.sample_executor.execute_samples(selected_files)
            self.sample_executor.print_summary()
            
            return self.file_selector.get_file_selections("samples")
            
        except ValueError as e:
            print(f"❌ 샘플 모드 오류: {str(e)}")
            return None
    
    def _select_from_directory(self):
        """디렉토리에서 파일 선택
        
        Requirements: 1.1, 1.2, 1.3, 1.4
        """
        directory = input("\n디렉토리 경로를 입력하세요: ").strip()
        
        if not directory:
            print("경로가 입력되지 않았습니다.")
            return None
        
        try:
            # 디렉토리 스캔
            print(f"\n📁 '{directory}' 스캔 중...")
            python_files = self.file_selector.scan_directory(directory)
            
            if not python_files:
                print("Python 파일을 찾을 수 없습니다.")
                return None
            
            print(f"\n발견된 Python 파일 ({len(python_files)}개):")
            for i, file_path in enumerate(python_files, 1):
                print(f"  {i}. {Path(file_path).name}")
            
            # 파일 선택
            print("\n선택할 파일 번호를 입력하세요 (쉼표로 구분, 'all'은 전체 선택):")
            selection = input("선택: ").strip()
            
            if selection.lower() == 'all':
                selected_indices = list(range(len(python_files)))
            else:
                try:
                    selected_indices = [int(x.strip()) - 1 for x in selection.split(',')]
                except ValueError:
                    print("잘못된 입력입니다.")
                    return None
            
            # 선택된 파일 추가
            for idx in selected_indices:
                if 0 <= idx < len(python_files):
                    self.file_selector.select_file(python_files[idx])
            
            selected_files = self.file_selector.get_selected_files()
            
            # 선택 검증
            if not self.file_selector.validate_selection():
                print("❌ 최소 1개 이상의 파일을 선택해야 합니다.")
                return None
            
            print(f"\n✓ {len(selected_files)}개의 파일이 선택되었습니다.")
            
            return self.file_selector.get_file_selections(directory)
            
        except ValueError as e:
            print(f"❌ 오류: {str(e)}")
            return None
    
    def _create_zip_archive(self, file_selections):
        """ZIP 아카이브 생성
        
        Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
        """
        print("\n" + "=" * 60)
        print("ZIP 아카이브 생성")
        print("=" * 60)
        
        try:
            print("\n📦 ZIP 압축 중...")
            archive_info = self.zip_builder.create_archive(file_selections)
            
            # 아카이브 검증
            if not self.zip_builder.validate_archive(archive_info.archive_path):
                print("❌ ZIP 아카이브 검증 실패")
                return None
            
            # 아카이브 정보 표시
            print("\n" + self.zip_builder.display_archive_info(archive_info))
            
            return archive_info
            
        except Exception as e:
            error_msg = self.zip_builder.handle_compression_error(e)
            print(f"\n{error_msg}")
            return None
    
    def _upload_to_watsonx(self, archive_path):
        """watsonx.ai에 업로드
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        print("\n" + "=" * 60)
        print("watsonx.ai 업로드")
        print("=" * 60)
        
        try:
            # 업로더 초기화 및 인증
            print("\n🔐 watsonx.ai 인증 중...")
            self.uploader = WatsonxUploader(self.config)
            
            if not self.uploader.authenticate():
                print("❌ 인증 실패")
                return None
            
            print("✓ 인증 완료")
            
            # 진행 상황 콜백
            def progress_callback(progress):
                percent = int(progress * 100)
                bar_length = 40
                filled = int(bar_length * progress)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r업로드 진행: [{bar}] {percent}%", end='', flush=True)
            
            # 재시도 로직 포함 업로드
            print("\n📤 업로드 중...")
            upload_result = self.uploader.retry_upload(
                archive_path,
                progress_callback=progress_callback
            )
            
            print()  # 줄바꿈
            
            if upload_result.success:
                print("✓ 업로드 완료")
                return upload_result
            else:
                print(f"❌ 업로드 실패: {upload_result.error_message}")
                return upload_result
                
        except Exception as e:
            print(f"\n❌ 업로드 중 오류 발생: {str(e)}")
            return None
        finally:
            if self.uploader:
                self.uploader.close()
    
    def _upload_to_github(self, archive_path):
        """GitHub에 업로드
        
        Requirements: GitHub 업로드 기능
        """
        if not self.config.github_upload_enabled:
            return None
        
        if not self.config.github_repo_url:
            print("❌ GitHub 저장소 URL이 설정되지 않았습니다")
            print("   GITHUB_REPO_URL 환경 변수를 설정하세요")
            return None
        
        if not self.config.github_token:
            print("❌ GitHub 토큰이 설정되지 않았습니다")
            print("   다음 단계를 따라 토큰을 생성하고 설정하세요:")
            print("   1. https://github.com/settings/tokens 접속")
            print("   2. 'Generate new token (classic)' 선택")
            print("   3. 'repo' 권한 선택")
            print("   4. 생성된 토큰을 GITHUB_TOKEN 환경 변수에 설정")
            return None
        
        try:
            print("\n🔐 GitHub 업로드 준비 중...")
            github_uploader = GitHubUploader(
                self.config.github_repo_url,
                self.config.github_token
            )
            
            # 파일명 생성
            from pathlib import Path
            zip_filename = Path(archive_path).name
            
            # 진행 상황 콜백
            def progress_callback(progress):
                percent = int(progress * 100)
                bar_length = 40
                filled = int(bar_length * progress)
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\rGitHub 업로드: [{bar}] {percent}%", end='', flush=True)
            
            # GitHub 업로드
            print(f"\n📤 GitHub에 업로드 중... ({zip_filename})")
            upload_result = github_uploader.retry_upload(
                archive_path,
                target_path=zip_filename,
                commit_message=f"Upload pipeline archive: {zip_filename}",
                progress_callback=progress_callback
            )
            
            print()  # 줄바꿈
            
            if upload_result.success:
                print("✓ GitHub 업로드 완료")
                return upload_result
            else:
                print(f"❌ GitHub 업로드 실패: {upload_result.error_message}")
                
                # 토큰 관련 오류인 경우 추가 안내
                if "토큰" in upload_result.error_message or "401" in upload_result.error_message:
                    print("\n💡 GitHub 토큰 설정 방법:")
                    print("   1. https://github.com/settings/tokens 접속")
                    print("   2. 'Generate new token (classic)' 선택")
                    print("   3. 'repo' 권한 선택")
                    print("   4. 생성된 토큰을 .env 파일의 GITHUB_TOKEN에 설정")
                
                return upload_result
                
        except Exception as e:
            print(f"\n❌ GitHub 업로드 중 오류 발생: {str(e)}")
            return None
    
    def _display_github_completion(self, github_result):
        """GitHub 업로드 완료 메시지 표시"""
        print("\n" + "=" * 60)
        print("GitHub 업로드 완료")
        print("=" * 60)
        print(f"\n✓ 파일 URL: {github_result.asset_url}")
        print(f"✓ Raw URL: {github_result.error_message}")  # Raw URL이 error_message에 저장됨
        print(f"✓ 업로드 시간: {github_result.upload_time:.2f}초")
        print(f"✓ 파일 크기: {github_result.file_size / (1024 * 1024):.2f} MB")
        
        # watsonx.ai 노트북에서 사용할 코드 예시 제공
        raw_url = github_result.error_message  # Raw URL
        print(f"\n📋 watsonx.ai 노트북에서 사용할 코드:")
        print("=" * 60)
        print("```python")
        print("import urllib.request")
        print("import zipfile")
        print("import sys")
        print("")
        print(f'# GitHub에서 ZIP 다운로드')
        print(f'urllib.request.urlretrieve(')
        print(f'    "{raw_url}",')
        print(f'    "/tmp/pipeline.zip"')
        print(f')')
        print("")
        print("# 압축 해제")
        print('with zipfile.ZipFile("/tmp/pipeline.zip", "r") as z:')
        print('    z.extractall("/tmp/pipeline")')
        print("")
        print("# Python 경로 추가")
        print('sys.path.insert(0, "/tmp/pipeline")')
        print("")
        print("# 파이프라인 실행")
        print("import main")
        print("main.run_pipeline()")
        print("```")
        print("=" * 60)
    
    def _display_completion(self, upload_result):
        """완료 메시지 표시
        
        Requirements: 6.5
        """
        print("\n" + "=" * 60)
        print("워크플로우 완료")
        print("=" * 60)
        print(f"\n✓ Asset ID: {upload_result.asset_id}")
        print(f"✓ Asset URL: {upload_result.asset_url}")
        print(f"✓ 업로드 시간: {upload_result.upload_time:.2f}초")
        print(f"✓ 파일 크기: {upload_result.file_size / (1024 * 1024):.2f} MB")
        print("\n모든 작업이 성공적으로 완료되었습니다!")
        print("=" * 60)


def main():
    """메인 진입점"""
    workflow = PipelineWorkflow()
    workflow.run()


if __name__ == "__main__":
    main()

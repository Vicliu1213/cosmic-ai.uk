# 數據壓縮和虛擬化管理
import os
import gzip
import json
import pickle
import tarfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
import hashlib
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, base_dir: str = "/root/comic_ai", use_distributed: bool = False):
        self.base_dir = Path(base_dir)
        self.compressed_dir = self.base_dir / "compressed_data"
        self.compressed_dir.mkdir(exist_ok=True)
        
        self.use_distributed = use_distributed
        self.ray_engine = None
        
        if use_distributed:
            try:
                from engine.ray_distributed_engine import RayDistributedEngine
                self.ray_engine = RayDistributedEngine()
                logger.info("✅ DataManager initialized with Ray distribution support")
            except Exception as e:
                logger.warning(f"Ray initialization failed: {e}")
                self.use_distributed = False
        
    def compress_file(self, file_path: str, compression_level: int = 6) -> str:
        """壓縮單個文件"""
        file_path = Path(file_path)
        compressed_path = self.compressed_dir / f"{file_path.name}.gz"
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                f_out.writelines(f_in)
        
        return str(compressed_path)
    
    def decompress_file(self, compressed_path: str, output_path: Optional[str] = None) -> str:
        """解壓縮文件"""
        compressed_path = Path(compressed_path)
        
        if output_path is None:
            output_path = self.base_dir / compressed_path.stem
        
        with gzip.open(compressed_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        return str(output_path)
    
    def create_archive(self, source_dir: str, archive_name: Optional[str] = None) -> str:
        """創建壓縮存檔"""
        source_dir = Path(source_dir)
        
        if archive_name is None:
            archive_name = f"{source_dir.name}.tar.gz"
        
        archive_path = self.compressed_dir / archive_name
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_dir, arcname=source_dir.name)
        
        return str(archive_path)
    
    def batch_compress(self, file_patterns: List[str] = None) -> Dict[str, str]:
        """批量壓縮文件（支持分布式）
        
        Args:
            file_patterns: 文件模式列表
            
        Returns:
            壓縮結果映射
        """
        if file_patterns is None:
            file_patterns = ["*.csv", "*.json", "*.txt", "*.log"]
        
        results = {}
        
        if self.use_distributed and self.ray_engine:
            # 分布式壓縮
            file_list = []
            for pattern in file_patterns:
                file_list.extend([
                    str(file_path) 
                    for file_path in self.base_dir.rglob(pattern) 
                    if file_path.is_file()
                ])
            
            if file_list:
                logger.info(f"Distributed compression of {len(file_list)} files")
                results = self.ray_engine.compress_in_parallel(
                    file_list,
                    self.compress_file
                )
            return results
        else:
            # 順序壓縮
            for pattern in file_patterns:
                for file_path in self.base_dir.rglob(pattern):
                    if file_path.is_file():
                        compressed = self.compress_file(str(file_path))
                        results[str(file_path)] = compressed
            
            return results
    
    def batch_decompress(self, compressed_paths: List[str]) -> Dict[str, str]:
        """批量解壓縮文件
        
        Args:
            compressed_paths: 壓縮文件路徑列表
            
        Returns:
            解壓縮結果映射
        """
        results = {}
        for compressed_path in compressed_paths:
            try:
                output_path = self.decompress_file(compressed_path)
                results[compressed_path] = output_path
            except Exception as e:
                logger.error(f"Decompression failed for {compressed_path}: {e}")
                results[compressed_path] = None
        
        return results
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """獲取存儲統計信息"""
        total_size = 0
        compressed_size = 0
        
        for file_path in self.base_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        for file_path in self.compressed_dir.rglob("*"):
            if file_path.is_file():
                compressed_size += file_path.stat().st_size
        
        compression_ratio = (compressed_size / total_size * 100) if total_size > 0 else 0
        
        return {
            "original_size_mb": total_size / (1024 * 1024),
            "compressed_size_mb": compressed_size / (1024 * 1024),
            "compression_ratio_percent": compression_ratio,
            "space_saved_mb": (total_size - compressed_size) / (1024 * 1024)
        }
    
    def distributed_batch_process(self, 
                                 file_paths: List[str],
                                 process_func: Callable) -> Dict[str, Any]:
        """分布式批量處理文件
        
        Args:
            file_paths: 文件路徑列表
            process_func: 處理函數
            
        Returns:
            處理結果
        """
        if not self.use_distributed or not self.ray_engine:
            return self._sequential_batch_process(file_paths, process_func)
        
        logger.info(f"Distributed processing of {len(file_paths)} files")
        return self.ray_engine.parallel_data_processing(
            file_paths,
            process_func
        )
    
    def _sequential_batch_process(self,
                                 file_paths: List[str],
                                 process_func: Callable) -> Dict[str, Any]:
        """順序批量處理文件
        
        Args:
            file_paths: 文件路徑列表
            process_func: 處理函數
            
        Returns:
            處理結果
        """
        results = {}
        for file_path in file_paths:
            try:
                result = process_func(file_path)
                results[file_path] = result
            except Exception as e:
                logger.error(f"Processing failed for {file_path}: {e}")
                results[file_path] = {'error': str(e)}
        
        return {
            'total_files': len(file_paths),
            'processed': len([r for r in results.values() if 'error' not in r]),
            'failed': len([r for r in results.values() if 'error' in r]),
            'details': results
        }
    
    def get_distributed_status(self) -> Dict[str, Any]:
        """獲取分布式狀態"""
        if not self.use_distributed or not self.ray_engine:
            return {'distributed': False, 'status': 'disabled'}
        
        return {
            'distributed': True,
            'status': 'active',
            'cluster': self.ray_engine.get_cluster_status()
        }
    
    def shutdown(self) -> None:
        """關閉分布式引擎"""
        if self.ray_engine:
            self.ray_engine.shutdown()

if __name__ == "__main__":
    dm = DataManager()
    
    # 批量壓縮數據
    print("🗜️ 開始壓縮數據...")
    results = dm.batch_compress()
    
    # 創建完整存檔
    print("📦 創建數據存檔...")
    archive = dm.create_archive("./data")
    
    # 顯示統計
    stats = dm.get_storage_stats()
    print(f"📊 壓縮統計:")
    print(f"   原始大小: {stats['original_size_mb']:.2f} MB")
    print(f"   壓縮後: {stats['compressed_size_mb']:.2f} MB")
    print(f"   節省空間: {stats['space_saved_mb']:.2f} MB")
    print(f"   壓縮率: {stats['compression_ratio_percent']:.1f}%")
#!/usr/bin/env python3
"""
Script para corrigir imports nos arquivos movidos para subpastas
"""
import os
import re

def fix_imports_in_file(file_path):
    """Corrige os imports em um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Padrão para encontrar sys.path.insert
        pattern = r'sys\.path\.insert\(0, os\.path\.dirname\(os\.path\.abspath\(__file__\)\)\)'
        
        # Substituir por 3 níveis acima (scripts/subfolder/file.py -> root)
        replacement = 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Corrigido: {file_path}")
            return True
        else:
            print(f"⚠️  Não encontrado padrão em: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Processa todos os arquivos Python nas subpastas"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Pastas para processar
    folders = [
        'scripts/development',
        'scripts/sync', 
        'scripts/enrichment',
        'scripts/testing',
        'utils'
    ]
    
    total_files = 0
    fixed_files = 0
    
    for folder in folders:
        folder_path = os.path.join(base_dir, folder)
        if os.path.exists(folder_path):
            print(f"\n📁 Processando pasta: {folder}")
            
            for filename in os.listdir(folder_path):
                if filename.endswith('.py'):
                    file_path = os.path.join(folder_path, filename)
                    total_files += 1
                    if fix_imports_in_file(file_path):
                        fixed_files += 1
    
    print(f"\n📊 Resumo:")
    print(f"   Total de arquivos: {total_files}")
    print(f"   Arquivos corrigidos: {fixed_files}")
    print(f"   Arquivos sem alteração: {total_files - fixed_files}")

if __name__ == '__main__':
    main()

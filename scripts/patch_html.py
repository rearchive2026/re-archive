import sys
import os
import re

def main():
    src_path = 're-archive-data/_pages/statistics.md'
    dest_path = 're-archive/statistics/index.html'
    
    with open(src_path, 'r', encoding='utf-8') as f:
        src_content = f.read()
    
    # Extract content between YAML front matter and the end
    content_match = re.search(r'---\s*\n.*?\n---\s*\n(.*)', src_content, re.DOTALL)
    if not content_match:
        print("Could not find content in source MD.")
        return
    
    new_payload = content_match.group(1).strip()
    
    # In index.html, replace everything between <article ...> and </article>
    # or more specifically between <section class="page__content ..."> and </section>
    with open(dest_path, 'r', encoding='utf-8') as f:
        dest_content = f.read()
    
    # We want to replace the part inside <section class="page__content e-content" itemprop="text"> ... </section>
    pattern = r'(<section class="page__content e-content" itemprop="text">).*?(</section>)'
    
    # Fix relative URLs in src
    new_payload = new_payload.replace('{{ \'/assets/js/vendor/crypto-js.min.js\' | relative_url }}', '/assets/js/vendor/crypto-js.min.js')
    new_payload = new_payload.replace('{{ "/assets/data/stats.json" | relative_url }}', '/assets/data/stats.json')
    
    patched_content = re.sub(pattern, r'\1\n' + new_payload + r'\n\2', dest_content, flags=re.DOTALL)
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(patched_content)
    
    print(f"Successfully patched {dest_path}")

if __name__ == "__main__":
    main()

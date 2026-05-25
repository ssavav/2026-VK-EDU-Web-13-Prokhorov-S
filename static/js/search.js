document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.search-input'); 
    
    if (!searchInput) return;

    const suggestionsBox = document.createElement('div');
    suggestionsBox.className = 'search-suggestions list-group position-absolute w-100';
    suggestionsBox.style.zIndex = '1000';
        suggestionsBox.style.top = '100%';
    
    searchInput.parentNode.classList.add('position-relative');
    searchInput.parentNode.appendChild(suggestionsBox);

    let debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value;

        if (query.length < 2) {
            suggestionsBox.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsBox.innerHTML = '';
                    if (data.suggestions.length > 0) {
                        data.suggestions.forEach(item => {
                            const link = document.createElement('a');
                            link.href = item.url;
                            link.className = 'list-group-item list-group-item-action';
                            link.textContent = item.title; 
                            suggestionsBox.appendChild(link);
                        });
                    } else {
                        suggestionsBox.innerHTML = '<div class="list-group-item text-muted">Nothing found...</div>';
                    }
                })
                .catch(error => console.error('Search error:', error));
        }, 300); 
    });

    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.innerHTML = '';
        }
    });

});
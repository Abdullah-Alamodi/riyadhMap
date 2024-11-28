document.addEventListener('DOMContentLoaded', function() {
    var searchBox = document.getElementById('search-box');
    var enterPressStore = document.getElementById('enter-press');

    searchBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            enterPressStore.value = true;
            enterPressStore.dispatchEvent(new Event('change'));
        }
    });
});
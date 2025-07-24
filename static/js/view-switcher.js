document.addEventListener('DOMContentLoaded', function() {
    // Initialize view switching
    initializeViewSwitching();
    
    // Initialize filters
    initializeFilters();
});

function initializeViewSwitching() {
    const viewButtons = document.querySelectorAll('[data-view], button:has(.fa-th-large), button:has(.fa-list), button:has(.fa-project-diagram)');
    const contentContainer = document.querySelector('.content-container') || document.querySelector('.grid-cols-2');
    
    // Set default view from localStorage or use grid
    const savedView = localStorage.getItem('preferredView') || 'grid';
    switchView(savedView, contentContainer, viewButtons);
    
    // Add event listeners to view buttons
    viewButtons.forEach(button => {
        let viewType = button.dataset.view;
        
        // If no data-view attribute, determine from icon
        if (!viewType) {
            if (button.querySelector('.fa-th-large')) viewType = 'grid';
            else if (button.querySelector('.fa-list')) viewType = 'list';
            else if (button.querySelector('.fa-project-diagram')) viewType = 'flow';
        }
        
        if (viewType) {
            button.setAttribute('data-view', viewType);
            button.addEventListener('click', function() {
                switchView(viewType, contentContainer, viewButtons);
            });
        }
    });
}

function switchView(viewMode, container, buttons) {
    if (!container) return;
    
    // Update active button styling
    buttons.forEach(btn => {
        btn.classList.remove('bg-blue-50', 'text-blue-700');
        btn.classList.add('hover:bg-gray-50', 'text-gray-700');
    });
    
    // Add active class to selected button
    const selectedButton = document.querySelector(`[data-view="${viewMode}"]`);
    if (selectedButton) {
        selectedButton.classList.remove('hover:bg-gray-50', 'text-gray-700');
        selectedButton.classList.add('bg-blue-50', 'text-blue-700', 'font-medium');
    }
    
    // Apply the appropriate layout
    container.className = container.className.replace(/grid-cols-\d+|flex flex-col|flow-layout/g, '');
    
    if (viewMode === 'grid') {
        container.classList.add('grid', 'grid-cols-2', 'gap-4');
    } else if (viewMode === 'list') {
        container.classList.add('flex', 'flex-col', 'space-y-4');
        
        // Adjust card styling for list view
        const cards = container.querySelectorAll('.border, .bg-white');
        cards.forEach(card => {
            card.classList.add('flex', 'justify-between');
        });
    } else if (viewMode === 'flow') {
        container.classList.add('flow-layout');
        // Add custom flow layout styling
        applyFlowLayout(container);
    }
    
    // Save preference
    localStorage.setItem('preferredView', viewMode);
}

function applyFlowLayout(container) {
    // Create a flow diagram layout
    // This is a simplified version - a real implementation would use a library like jsPlumb or dagre-d3
    
    const items = container.querySelectorAll('.border, .bg-white');
    
    // Clear existing content
    container.innerHTML = '';
    
    // Create flow container
    const flowContainer = document.createElement('div');
    flowContainer.className = 'relative min-h-[600px] border border-gray-200 rounded-lg p-4';
    
    // Add items in a flow pattern
    let left = 20;
    let top = 20;
    
    items.forEach((item, index) => {
        const clone = item.cloneNode(true);
        clone.style.position = 'absolute';
        clone.style.left = `${left}px`;
        clone.style.top = `${top}px`;
        clone.style.width = '300px';
        clone.classList.add('shadow-md');
        
        flowContainer.appendChild(clone);
        
        // Create connector lines
        if (index > 0) {
            const connector = document.createElement('div');
            connector.className = 'absolute border-t-2 border-blue-300';
            connector.style.width = '50px';
            connector.style.left = `${left - 50}px`;
            connector.style.top = `${top + 50}px`;
            flowContainer.appendChild(connector);
        }
        
        // Adjust position for next item
        if (index % 2 === 0) {
            left += 350;
        } else {
            left = 20;
            top += 150;
        }
    });
    
    container.appendChild(flowContainer);
}

function initializeFilters() {
    const filters = document.querySelectorAll('select[name="status"], select[name="cycle"], select[name="phase"], select[name="tech_stack"]');
    
    // If no filters exist, return early
    if (filters.length === 0) return;
    
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            applyFilters();
        });
    });
    
    // Add reset filters button
    const filtersContainer = document.querySelector('.filters') || 
        (document.querySelector('select[name="status"]')?.closest('div')?.parentElement);
    
    if (filtersContainer) {
        const resetButton = document.createElement('button');
        resetButton.className = 'w-full text-center px-3 py-2 mt-4 rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200';
        resetButton.textContent = 'Reset Filters';
        resetButton.addEventListener('click', resetFilters);
        
        filtersContainer.appendChild(resetButton);
    }
}

function applyFilters() {
    const status = document.querySelector('select[name="status"]')?.value;
    const cycle = document.querySelector('select[name="cycle"]')?.value;
    const phase = document.querySelector('select[name="phase"]')?.value;
    const techStack = document.querySelector('select[name="tech_stack"]')?.value;
    
    // Get all filterable items
    const items = document.querySelectorAll('.border, .bg-white');
    let visibleCount = 0;
    
    items.forEach(item => {
        // Get data attributes (add these to your templates)
        const itemStatus = item.getAttribute('data-status') || item.querySelector('.status-badge')?.textContent.trim();
        const itemCycle = item.getAttribute('data-cycle') || item.querySelector('.font-medium')?.textContent.trim();
        const itemPhase = item.getAttribute('data-phase');
        const itemTechStack = item.getAttribute('data-tech-stack');
        
        // Default to showing the item
        let shouldShow = true;
        
        // Apply filters
        if (status && itemStatus && !itemStatus.includes(status)) {
            shouldShow = false;
        }
        
        if (cycle && itemCycle && !itemCycle.includes(cycle)) {
            shouldShow = false;
        }
        
        if (phase && itemPhase && !itemPhase.includes(phase)) {
            shouldShow = false;
        }
        
        if (techStack && itemTechStack && !itemTechStack.includes(techStack)) {
            shouldShow = false;
        }
        
        // Show or hide based on filter results
        item.classList.toggle('hidden', !shouldShow);
        
        if (shouldShow) visibleCount++;
    });
    
    // Show "no results" message if needed
    let noResultsMsg = document.getElementById('no-filter-results');
    
    if (visibleCount === 0) {
        if (!noResultsMsg) {
            noResultsMsg = document.createElement('div');
            noResultsMsg.id = 'no-filter-results';
            noResultsMsg.className = 'col-span-full py-8 text-center text-gray-500';
            noResultsMsg.innerHTML = 'No items match your filters. <button class="text-blue-500 underline" onclick="resetFilters()">Reset filters</button>';
            
            const container = document.querySelector('.content-container') || document.querySelector('.grid-cols-2');
            container.appendChild(noResultsMsg);
        } else {
            noResultsMsg.classList.remove('hidden');
        }
    } else if (noResultsMsg) {
        noResultsMsg.classList.add('hidden');
    }
}

function resetFilters() {
    const filters = document.querySelectorAll('select[name="status"], select[name="cycle"], select[name="phase"], select[name="tech_stack"]');
    
    filters.forEach(filter => {
        filter.value = '';
    });
    
    applyFilters();
}

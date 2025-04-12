// This file is intended for general Navbar JavaScript functions,
// but currently contains no specific logic as ServerSelector was moved.

document.addEventListener('DOMContentLoaded', () => {
    console.log("Navbar JS DOMContentLoaded fired."); // Log: Check if script runs

    const clickDropdowns = document.querySelectorAll('.js-navbar-dropdown');

    if (clickDropdowns.length > 0) {
        console.log(`Initializing ${clickDropdowns.length} click-based navbar dropdowns.`);
        
        clickDropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.navbar-link');
            if (trigger) {
                console.log("Adding click listener to:", trigger); // Log: Check which triggers get listeners
                trigger.addEventListener('click', (event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    console.log("Dropdown trigger clicked:", trigger); // Log: Check if click is registered
                    
                    // Close other open dropdowns first
                    clickDropdowns.forEach(otherDropdown => {
                        if (otherDropdown !== dropdown && otherDropdown.classList.contains('is-active')) {
                             console.log("Closing other dropdown:", otherDropdown);
                             otherDropdown.classList.remove('is-active');
                        }
                    });
                    
                    // Toggle the current dropdown
                    const isActive = dropdown.classList.toggle('is-active');
                    console.log(`Toggled dropdown ${isActive ? 'ON' : 'OFF'}:`, dropdown); // Log: Check class toggle
                });
            } else {
                 console.warn("Could not find .navbar-link trigger for dropdown:", dropdown);
            }
        });

        // Add a listener to the document to close dropdowns when clicking outside
        document.addEventListener('click', (event) => {
            let clickedInsideDropdown = false;
            clickDropdowns.forEach(dropdown => {
                if (dropdown.contains(event.target)) {
                    clickedInsideDropdown = true;
                }
            });

            if (!clickedInsideDropdown) {
                // console.log("Clicked outside, closing dropdowns."); // Optional Log
                let closedAny = false;
                clickDropdowns.forEach(dropdown => {
                    if (dropdown.classList.contains('is-active')) {
                         dropdown.classList.remove('is-active');
                         closedAny = true;
                    }
                });
                // if (closedAny) console.log("Closed dropdowns due to outside click.");
            }
        });
        
    } else {
         console.log("No .js-navbar-dropdown elements found to initialize.");
    }
});

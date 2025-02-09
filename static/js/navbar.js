const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('active');
    
    // Toggle hamburger icon
    const icon = hamburger.querySelector('i');
    icon.classList.toggle('fa-bars');
    icon.classList.toggle('fa-times');
});

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname; // Current page path
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Loop through all the nav links
    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname; // Extract pathname from href
        
        // Check if linkPath matches the current page
        if (linkPath === currentPath) {
            link.classList.add('active');  // Add active class to link
            // Optionally, add active class to the icon inside the link
            const icon = link.querySelector('i');
            icon.classList.add('active');  // Ensure icon gets active styling too
        } else {
            link.classList.remove('active');  // Remove active class from other links
            const icon = link.querySelector('i');
            icon.classList.remove('active');  // Remove active styling from icon
        }
    });
});


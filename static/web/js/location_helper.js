function addOrRemovePincode(csrftoken, pincode=null) {
    $.ajax({
        type: "POST",
        url: "/location_pincode/",
        headers: { 'X-CSRFToken': csrftoken }, 
        data: { pincode: pincode },
        success: () => { window.location.replace(localStorage.getItem('currentUrl')) }
    })
}

function myGetLocation(locationData) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; 
   
    const lat = locationData.coords.latitude
   
    const long = locationData.coords.longitude
    console.log(lat,long ,'-----------------')
    $.ajax({
        url: `https://api.opencagedata.com/geocode/v1/json?q=${lat}+${long}&key=63a04d4ae8d04a9cba3e6e6efc71be04`,
        success: function(response) {
            pincode = response.results[0].components.postcode
            localStorage.setItem('haveLocation', true)
            addOrRemovePincode(csrftoken, pincode)
        }
    })
}

function handlePermission() {
    navigator.permissions.query({ name: 'geolocation' }).then((result) => {
        switch(result.state) {
            case 'prompt': 
                localStorage.setItem('haveLocation', false)
                navigator.geolocation.getCurrentPosition(myGetLocation);
                break
            case 'denied':
                document.getElementById('location-alert').style.display = 'block'
                break
            default:
                document.getElementById('location-alert').style.display = 'none'
        }
    
        result.addEventListener('change', () => {
            localStorage.setItem('currentUrl', window.location.href)

            if(result.state === 'denied' && localStorage.getItem('haveLocation')) {
                const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value

                localStorage.setItem('haveLocation', false)
                addOrRemovePincode(csrftoken)
            } else if(localStorage.getItem('haveLocation') == 'false' && result.state === 'granted') {
                navigator.geolocation.getCurrentPosition(myGetLocation);
            }
        });
    });
}
    
handlePermission()
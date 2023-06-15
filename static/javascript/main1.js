const ShowProfBtn =  document.getElementById('show-profile')

const ProfileSec = document.getElementById('profile-section')

const main =  document.getElementById('main')

// const main1 = document.getElementById('main1')

// const main2 = document.getElementById('main2')


// const button = document.getElementById('button')

const ClsProfileBtn = document.getElementById('close')

ShowProfBtn.addEventListener('click', function (){
	ProfileSec.style.display ='block'
	main.style.display = 'none'

})


ClsProfileBtn.addEventListener('click', function (){
	ProfileSec.style.display = 'none'
	main.style.display = 'block'
})

// botton.addEventListener('click', function(){
// 	main1.style.display = 'none';
// 	main2.style.display = 'block'

// })
window.onload = function() {
	document.getElementById('focus').focus();

}
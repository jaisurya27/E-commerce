from django.shortcuts import render

# Create your views here.

def Homepage(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, "store/home.html", context)

def mail_send(subject,message,email_from,recipient_list):
    send_mail( subject, message, email_from, recipient_list)


def SignUp(request):
    if request.method == 'POST':
        form = request.POST.get("name")
        if form.isvalid():
            user_obj = form.save()
            user_obj.email = form.cleaned_data.get["email"]
            user_obj.username = form.cleaned_data.get('username')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password1')
            user_obj.verificationid = generateOTP()
            # user = authenticate(email=email, password=password)

            if user.objects.filter(email=user_obj.email).exists():
                messages.info(request,'email-id already exists')
                return render(request,"signup.html")
            elif password1 != password2:
                raise ValidationError("Passwords don't match")
            else :
                user_obj.save()
                mail_send('Verification Mail','Your Verification Number is : ' + str(user_obj.verificationid),settings.EMAIL_HOST_USER,[user_obj.email, ])
                return redirect('activateUser',uid = urlsafe_base64_encode(force_bytes(user_obj.pk)))
                # if request.POST.get("otp")== user_obj.verificationid :
                #     login(request, user)
                #     return render(request, "signup.html",{'form' : form})
        else:
            return render(request,'error.html',{'text':'Data Entered is Invalid...'})


def SignIn(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(username=email,password=password)
        if user.is_verified:
                auth.login(request,user,backend=None)
                add_message(request,'Logged In Successfully!!!')
                profile = Profile.objects.filter(user=request.user).first()
                return redirect('home.html')
        else:
            return redirect('activateUser',uid = urlsafe_base64_encode(force_bytes(jsuser.user.pk)))
    else:
        return render(request,'store/login.html')

def generateOTP():
    digits = "0123456789"
    OTP = ""
    for _ in range(6) : 
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def forgotPassword(request,uid):
    if request.method == 'POST':
        try:
            pk = urlsafe_base64_decode(uid).decode()
            user = UserModel._default_manager.get(pk=pk)
        except(TypeError, ValueError, OverflowError):
            user = None
        newpwd = request.POST['newpwd']
        verid = request.POST['verid']
        if verid == request.session[uid] and user is not None:
            user.set_password(newpwd)
            user.save()
            Notifications(receiver=user,message='Password Changed Successfully!!!').save()
            del request.session[uid]
            return render(request,'store/error.html',{'text':'Password Changed Successfully! Now You Can Login...'})
        elif verid != request.session[uid]:
            return render(request,'store/error.html',{'text':'Verification Id Mismatch'})
        else:
            return render(request,'store/error.html',{'text':'Credentials wrong'})
    else: 
        return render(request,'store/forgotpassword.html')

def ViewProfile(request):
    if request.user.is_authenticated():
        return render('profile.html')
        
def EditProfile(request):
    user = request.user
    form = forms.UserProfileUpdateForm(instance = user.profile)
    if request.method == 'POST':
        form = forms.UserProfileUpdateForm(instance = user.profile, data = request.POST, files = request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"your profile has been updated")
            return redirect('profile')
    return render(request,'editprofile.html',{form:'form'})
from django.shortcuts import render,redirect,HttpResponse
from dasapp.models import DoctorReg,Specialization,CustomUser,Appointment,Page,PatientReg
from django.http import JsonResponse
import random
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

def USERBASE(request):
    
    return render(request, 'userbase.html',context)



def PATIENTREGISTRATION(request):
    if request.method == "POST":
        pic = request.FILES.get('pic')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        mobno = request.POST.get('mobno')
        gender = request.POST.get('gender')
        username = request.POST.get('username')
        address = request.POST.get('address')
        password = request.POST.get('password')

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request,'Email already exist')
            return redirect('patreg')
        
        else:
            user = CustomUser(
               first_name=first_name,
               last_name=last_name,
               username=username,
               email=email,
               user_type=3,
               profile_pic = pic,
            )
            user.set_password(password)
            user.save()
            
            patient = PatientReg(
                admin = user,
                mobilenumber = mobno,
                gender = gender,
                address = address,
            )
            patient.save()            
            messages.success(request,'Signup Successfully')
            return redirect('patreg')
    

    return render(request, 'user/patient-reg.html')

def PATIENTHOME(request):
    doctor_count = DoctorReg.objects.all().count
    specialization_count = Specialization.objects.all().count
    context = {
        'doctor_count':doctor_count,
        'specialization_count':specialization_count,

    } 
    return render(request,'user/userhome.html',context)

def Index(request):
    doctorview = DoctorReg.objects.all()
    first_page = Page.objects.first()

    context = {'doctorview': doctorview,
    'page':first_page,
    }
    return render(request, 'index.html',context)

def Doctor(request):
    doctorview = DoctorReg.objects.all()
    first_page = Page.objects.first()

    context = {'dv': doctorview,
    'page':first_page,
    }
    return render(request, 'doctor.html',context)

def Aboutus(request):
   
    first_page = Page.objects.first()

    context = {
    'page':first_page,
    }
    return render(request, 'aboutus.html',context)

def Contactus(request):
   
    first_page = Page.objects.first()

    context = {
    'page':first_page,
    }
    return render(request, 'contactus.html',context)

def get_doctor(request):
    if request.method == 'GET':
        s_id = request.GET.get('s_id')
        doctors = DoctorReg.objects.filter(specialization_id=s_id)
        
        doctor_options = ''
        for doc in doctors:
            doctor_options += f'<option value="{doc.id}">{doc.admin.first_name}</option>'
        
        return JsonResponse({'doctor_options': doctor_options})

from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
import random

import stripe
from django.conf import settings

from django.shortcuts import render, redirect
from django.contrib import messages
import stripe
from django.conf import settings
from datetime import datetime, timedelta
import random

def create_appointment(request):
    specialization = Specialization.objects.all()

    if request.method == "POST":
        try:
            appointmentnumber = random.randint(100000000, 999999999)
            spec_id = request.POST.get('spec_id')
            doctor_id = request.POST.get('doctor_id')
            date_of_appointment = request.POST.get('date_of_appointment')
            time_of_appointment = request.POST.get('time_of_appointment')
            additional_msg = request.POST.get('additional_msg')

            doc_instance = DoctorReg.objects.get(id=doctor_id)
            spec_instance = Specialization.objects.get(id=spec_id)
            patient_instance = PatientReg.objects.get(admin=request.user.id)

            appointment_date = datetime.strptime(date_of_appointment, '%Y-%m-%d').date()
            today_date = timezone.now().date()

            # Ensure appointment is not on Sunday
            if appointment_date.weekday() == 6:  # Sunday is represented as 6
                messages.error(request, "Appointments cannot be booked on Sundays.")
                return redirect('patientappointment')

            # Ensure appointment is in the future
            if appointment_date <= today_date:
                messages.error(request, "Please select a future date for your appointment")
                return redirect('patientappointment')

            # Convert input time to datetime object
            appointment_time = datetime.strptime(time_of_appointment, '%H:%M').time()

            # Ensure the appointment is between 10 AM and 4 PM
            start_time = datetime.strptime("10:00", '%H:%M').time()
            end_time = datetime.strptime("16:00", '%H:%M').time()
            if not (start_time <= appointment_time <= end_time):
                messages.error(request, "Appointments can only be booked between 10 AM and 4 PM.")
                return redirect('patientappointment')

            # Check for existing appointment at the same time
            existing_appointment = Appointment.objects.filter(
                doctor_id=doc_instance,
                date_of_appointment=date_of_appointment,
                time_of_appointment=time_of_appointment
            ).exists()

            if existing_appointment:
                latest_appointment = Appointment.objects.filter(
                    doctor_id=doc_instance,
                    date_of_appointment=date_of_appointment
                ).order_by('-time_of_appointment').first()

                if latest_appointment:
                    latest_time = datetime.strptime(str(latest_appointment.time_of_appointment), '%H:%M:%S').time()
                    next_available_time = (datetime.combine(appointment_date, latest_time) + timedelta(minutes=15)).time()
                    next_available_time_str = next_available_time.strftime('%H:%M')

                    messages.error(request, f"This slot is booked. Next available: {next_available_time_str}.")
                    return redirect('patientappointment')

            # Create appointment with pending payment status
            appointment = Appointment.objects.create(
                appointmentnumber=appointmentnumber,
                pat_id=patient_instance,
                spec_id=spec_instance,
                doctor_id=doc_instance,
                date_of_appointment=date_of_appointment,
                time_of_appointment=time_of_appointment,
                additional_msg=additional_msg,
                status="Pending Payment"
            )

            # Stripe payment integration
            stripe.api_key = settings.STRIPE_SECRET_KEY
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(doc_instance.fee * 100),
                        'product_data': {
                            'name': f"Appointment with {doc_instance.admin.first_name}",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/payment-success/') + f"?appointment_id={appointment.id}",
                cancel_url=request.build_absolute_uri('/payment-failed/') + f"?appointment_id={appointment.id}",
            )

            return redirect(checkout_session.url, code=303)

        except (DoctorReg.DoesNotExist, Specialization.DoesNotExist, PatientReg.DoesNotExist):
            messages.error(request, "Invalid data. Please check your selections.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('patientappointment')

    return render(request, 'user/appointment.html', {'specialization': specialization})




def View_Appointment_History(request):
    pat_reg = request.user
    pat_admin = PatientReg.objects.get(admin=pat_reg)
    userapptdetails = Appointment.objects.filter(pat_id=pat_admin)
    context = {
        'vah':userapptdetails
    }
    return render(request, 'user/appointment-history.html', context)

def cancel_appointment(request, id):
    try:
        appointment = Appointment.objects.get(id=id, pat_id=request.user.patientreg)
        if appointment.status != 'Approved':
            appointment.status = 'Canceled'
            appointment.save()
            messages.success(request, "Your appointment has been canceled successfully.")
        else:
            messages.error(request, "You cannot cancel this appointment.")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")
    return redirect('view_appointment_history')

def User_Search_Appointments(request):
    page = Page.objects.all()
    
    if request.method == "GET":
        query = request.GET.get('query', '')
        if query:
            # Filter records where fullname or Appointment Number contains the query
            patient = Appointment.objects.filter(fullname__icontains=query) | Appointment.objects.filter(appointmentnumber__icontains=query)
            messages.info(request, "Search against " + query)
            context = {'patient': patient, 'query': query, 'page': page}
            return render(request, 'search-appointment.html', context)
        else:
            print("No Record Found")
            context = {'page': page}
            return render(request, 'search-appointment.html', context)
    
    # If the request method is not GET
    context = {'page': page}
    return render(request, 'search-appointment.html', context)
def View_Appointment_Details(request,id):
    page = Page.objects.all()
    patientdetails=Appointment.objects.filter(id=id)
    context={'patientdetails':patientdetails,
    'page': page

    }

    return render(request,'user_appointment-details.html',context)


def payment_success(request):
    appointment_id = request.GET.get('appointment_id')
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = "Confirmed"
        appointment.save()
        messages.success(request, "Payment successful. Your appointment is confirmed.")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")

    return redirect('view_appointment_history')


def payment_failed(request):
    appointment_id = request.GET.get('appointment_id')
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        appointment.status = "Payment Failed"
        appointment.save()
        messages.error(request, "Payment failed. Please try again.")
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found.")

    return redirect('patientappointment')

from django.shortcuts import render
#from django.template import RequestContext
from myapp.forms import UploadFileForm
from PIL import Image, ImageOps,ImageFilter
import os.path
from myapp.s3upload import upload_to_s3_bucket_path


PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#~/Desktop/imagepro/

def applyfilter (filename, preset):
    inputfile = os.path.join(PROJECT_ROOT, 'media', filename)

    f=filename.split('.')
    outputfilename = f[0] + '-out.jpg'

    outputfile = os.path.join(PROJECT_ROOT, 'myapp', 'templates', 'static', 'output', outputfilename)

    im = Image.open(inputfile)
    if preset=='gray':
        im = ImageOps.grayscale(im)

    if preset=='edge':
        im = ImageOps.grayscale(im)
        im = im.filter(ImageFilter.FIND_EDGES)

    if preset=='poster':
        im = ImageOps.posterize(im, 3)

    if preset=='solar':
        im = ImageOps.solarize(im, threshold=80)

    if preset=='blur':
        im = im.filter(ImageFilter.BLUR)

    if preset=='sepia':
        sepia = []
        r, g, b = (239, 224, 185)
        for i in range(255):
            sepia.extend((r*i//255, g*i//255, b*i//255))
        im = im.convert("L")
        im.putpalette(sepia)
        im = im.convert("RGB")

    im.save(outputfile)
    return outputfilename


def handle_uploaded_file(f,preset):
    uploadfilename='media/' + f.name
    with open(uploadfilename, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    outputfilename=applyfilter(f.name, preset)
    return outputfilename


def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            preset=request.POST['preset']
            outputfilename = handle_uploaded_file(request.FILES['myfilefield'],preset)
            upload_to_s3_bucket_path('tlhuynhbucket', '/home/ec2-user/imageProcessing/myapp/templates/static/output',outputfilename)
            return render(request, 'process.html', {'outputfilename': outputfilename})
    else:
        form = UploadFileForm()
    return render(request, 'index.html', {'form': form})


def process(request):
    return render(request,'process.html', {})

from stegano import lsb
from stegano.lsb import generators

# message = 'Hi there , Suhin is here'
# hide = lsb.hide('flower.jpg', message, generators.eratosthenes())
# hide.save('hidden_image.png')

unhide = lsb.reveal('hidden_image.png', generators.eratosthenes())
print(unhide)
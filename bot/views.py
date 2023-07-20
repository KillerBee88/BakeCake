from django.shortcuts import get_object_or_404
from datacenter.models import Cake


def verify_cake(cake_id):
	cake = get_object_or_404(Cake, id=int(cake_id))
	for param in cake.get_params():
		if not param.is_available:
			return False
	return True


import string
import random

from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import Http404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, TemplateView
from django import forms

from doodler.models import Doodle


class ObjMixin:
    def get_obj(self):
        try:
            obj = Doodle.objects.get(id=self.kwargs["doodle"])
        except Doodle.DoesNotExist:
            raise Http404
        return obj


class HomeForm(forms.Form):
    name = forms.CharField()


def make_password():
    alpha = string.ascii_letters + string.digits
    return "".join(random.choice(alpha) for _ in range(16))


class HomeView(FormView):
    form_class = HomeForm
    template_name = "home.html"

    def form_valid(self, form):
        choices = self.request.POST.getlist("choice")
        choices = [c.strip() for c in choices if c.strip()]
        if len(choices) == 0:
            form.add_error(None, "You must have at least one (non-empty) choice")
            return self.form_invalid(form)

        new_object = Doodle.objects.create(
            name=form.cleaned_data["name"], data={"choices": choices, "answers": [], "owner_password": make_password()}
        )
        return HttpResponseRedirect(new_object.owner_link())


class AnswerForm(forms.Form):
    name = forms.CharField()


class AnswerView(FormView, ObjMixin):
    form_class = AnswerForm
    template_name = "answer.html"

    def get_context_data(self, **kwargs):
        obj = self.get_obj()
        choices = [
            {"key": f"choice{i}", "name": choice}
            for i, choice in enumerate(obj.data["choices"])
        ]

        return super().get_context_data(doodle=obj, choices=choices, **kwargs)

    def form_valid(self, form):
        obj = self.get_obj()
        answers = []
        for i, _ in enumerate(obj.data["choices"]):
            answer = self.request.POST.get(f"choice{i}")
            if answer:
                answers.append("yes")
            else:
                answers.append("no")

        data = obj.data
        data["answers"].append({"name": form.cleaned_data["name"], "choices": answers})
        obj.data = data
        obj.last_activity = timezone.now()
        obj.save()

        return HttpResponseRedirect(reverse("thanks", kwargs={"doodle": obj.id}))


class OwnerView(TemplateView, ObjMixin):
    template_name = "owner.html"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_obj()
        supplied = request.GET.get("secretOwnerPassword")
        expected = obj.data.get("owner_password")
        if not supplied or expected != supplied:
            return HttpResponseForbidden("Wrong owner password".encode())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        obj = self.get_obj()

        choices = [{"name": c, "count": 0, "is_max": False} for c in obj.data["choices"]]
        answers = []
        for answer in obj.data["answers"]:
            answers.append({"name": answer["name"], "choices": []})
            for choice, a in zip(choices, answer["choices"]):
                if a == "yes":
                    answers[-1]["choices"].append(True)
                    choice["count"] += 1
                else:
                    answers[-1]["choices"].append(False)
        max_count = max(c["count"] for c in choices)
        for c in choices:
            if c["count"] == max_count:
                c["is_max"] = True
        return super().get_context_data(doodle=obj, choices=choices, answers=answers)


class ThanksView(TemplateView, ObjMixin):
    template_name = "thanks.html"

    def get_context_data(self, **kwargs):
        obj = self.get_obj()
        return super().get_context_data(doodle=obj, choices=obj.data["choices"])

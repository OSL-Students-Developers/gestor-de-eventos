# -*- coding: utf-8 -*-

# Evenge - gestor de eventos (events management)
# Copyright (C) 2014 - desarrollo.evenge@gmail.com
# Carlos Campos Fuentes | Francisco Javier Exposito Cruz | Ivan Ortega Alba | Victor Coronas Lara
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
################################################################
"""Modulo de inicio.Básicamente maneja las URL, renderiza la plantilla
correspondiente y pása los parametros a dicha plantilla. Cada clase corresponde
a una URL. Ver clase par más información.
   :author: Carlos Campos Fuentes | Francisco Javier Exposito Cruz | Ivan Ortega Alba | Victor Coronas Lara
   :version: 0.1"""

import os
import urllib
from google.appengine.ext import ndb
from _oo.classes.evento import Evento
from _oo.model import controladorEvento
from _oo.model import controladorUsuario
from _oo.model import controladorPonente
import jinja2
import webapp2
import hashlib
import json


class Index(webapp2.RequestHandler):
    """Es llamada por /"""
    def get(self):
        """
        Devuelve el index en función del logueo del usuario.
        Si está logueado o no
        """
        usuario = controladorUsuario.getUsuarioLogeado(self)
        if usuario:
            eventos = controladorEvento.getEventosAsociados(usuario.key.id())
            template_values = {'usuario': usuario, 'eventos': eventos}
            template = JINJA_ENVIRONMENT.get_template('templates/templateMyEvents.html')
            self.response.write(template.render(template_values))
        else:
            template_values = {}
            template = JINJA_ENVIRONMENT.get_template('templates/indexVisitante.html')
            self.response.write(template.render(template_values))

class InsertarEvento(webapp2.RequestHandler):
    """Es llamada por /iEvento. """
    def get(self):
        """
        Por GET devuelve el formulario para insertar eventos
        """
        user = controladorUsuario.getUsuarioLogeado(self)
        if user == False:
            self.redirect('/login')
        else:
            template_values = {'usuario':int(controladorUsuario.getKey(user))}
            template = JINJA_ENVIRONMENT.get_template('templates/templateNewEvent.html')
            self.response.write(template.render(template_values))

    def post(self):
        """
        Por POST recoge los datos del formulario del nuevo evento, y inserta en BD.
        """
        nombre = self.request.get('nombre')
        hora = self.request.get('hora')
        fecha = self.request.get('fecha')
        cantidadAsistentes = self.request.get('cantidadAsistentes')
        descripcion = self.request.get('descripcion').strip()
        lugar = self.request.get('lugar')
        asistencia = self.request.get('asistencia')
        lat = self.request.get('latitud')
        lon = self.request.get('longitud')
        privado = self.request.get('privado')
        idCreador = self.request.get('idUser')
        ret = controladorEvento.SetEvento(nombre, 1, privado,
        idCreador, hora, fecha,
        cantidadAsistentes, lugar, lat,
        lon, descripcion, asistencia)
        # Aquí se avisaría por email
        resp = {'response': True, 'idEvento': ret}
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(resp))


class InsertarPonente(webapp2.RequestHandler):
    """Es llamada por /iPonente. """

    def get(self):
        """Devuelve el formulario para registrar un nuevo ponente"""
        user = controladorUsuario.getUsuarioLogeado(self)
        if user is False:
            self.redirect('/login')
        else:
            template_values = {}
            template = JINJA_ENVIRONMENT.get_template('templates/templatesNewPonente.html')
            self.response.write(template.render(template_values))

    def post(self):
        """Inserta un nuevo ponente con los datos recogidos"""
        nombre = self.request.get("nombre").strip()
        apellidos = self.request.get("apellidos").strip()
        email = self.request.get("email").strip()
        telefono = self.request.get("telefono").strip()
        twitter = self.request.get("twitter").strip()
        web = self.request.get("web").strip()
        idNuevoPonente = controladorPonente.nuevoRegistroPonente(
            nombre, apellidos,
            email, telefono,
            twitter, web)
        self.redirect('/')

# class Evenge(webapp2.RequestHandler):
#     def hazElCuadrado(self, numero):
#         return numero*numero
#
#     def testPonente(self, ponente):
#         ponente.put()
#         query = Ponente.query(Ponente.email == 'pepito@jemail.com')
#         email = query.email
#         query.delete
#         return email
#
#     def testInsertarEvento(self, evento):
#         evt = evento
#         evt.put()
#         return True
#
#     def testInsertarUsuario(self, usuario):
#         u = usuario
#         u.put()
#         return True


class MostrarEvento(webapp2.RequestHandler):
    """Es llamada por /miseventos."""

    def get(self):
        """Pasa a plantilla un evento del usuario identificado por un id,
            recibido por GET en la variable idEvento.
            La información a la plantilla es:
            - objeto Evento
            - Usuario logueado : true o false
            - Usuario Creador
            - id del evento
            - numero de eventos del usuario
            - objeto Usuario (logeado en este momento)
            - asistentes : Vector de objetos Asistente, correspondiente al evento

        """
        userLogin = False
        userCreador = False
        user = controladorUsuario.getUsuarioLogeado(self)
        idEvento = self.request.get('id')
        evento = controladorEvento.GetEventoById(idEvento)
        asistentes = controladorEvento.getAsistentesEvento(idEvento);
        if user is not False:
            userLogin = True
            numeroEventos = controladorEvento.getEventosAsociadosCount(controladorUsuario.getKey(user))
        if str(controladorUsuario.getKey(user)) == str(evento.idCreador):
            userCreador = True
        template_values = {'evento': evento,
                           'userLogin': userLogin,
                           'descripcion': evento.descripcion.replace("\n", "<br />"),
                           'userCreador': userCreador,
                           'numeroEventos': numeroEventos,
                           'id': idEvento,
                           'usuario': user,
                           'asistentes': asistentes}
        template = JINJA_ENVIRONMENT.get_template('templates/templateEvents.html')
        self.response.write(template.render(template_values))


class MostrarInforme(webapp2.RequestHandler):
    """Es llamada por /misinformes."""

    def get(self):
        """
        Muestra la plantilla, por ahora sin datos, de la generación de informes.
        """
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/templateReports.html')
        self.response.write(template.render(template_values))


class MostrarMiCuenta(webapp2.RequestHandler):
    """Es llamada por /micuenta"""

    def get(self):
        """
        Devuelve la plantilla con los datos de usuario.
        Se pasan los datos:
            - objeto Usuario : usuario logueado
            - numeroEventos : numero de eventos activos de este usuario
        """
        userLogin = False
        user = controladorUsuario.getUsuarioLogeado(self)
        if user is not False:
            userLogin = True
            numeroEventos = controladorEvento.getEventosAsociadosCount(controladorUsuario.getKey(user))
        usuario = controladorUsuario.getUsuarioLogeado(self)
        template_values = {'usuario': usuario,
                            'numeroEventos': numeroEventos,
                            'userLogin': userLogin}
        template = JINJA_ENVIRONMENT.get_template('templates/templateUser.html')
        self.response.write(template.render(template_values))


class MostrarMisEventos(webapp2.RequestHandler):
    """Es llamada por /miseventos"""

    def get(self):
        """
        Muestra TODOS los eventos asociados al usuario logueado en este momento.
        Se pasan los datos:
            - vector Eventos : Colección de todos los objeto Evento del usuario
        """
        usuarioLogeado = controladorUsuario.getUsuarioLogeado(self)
        eventos = controladorEvento.getEventosAsociados(usuarioLogeado.key.id())
        template_values = {'eventos': eventos}
        template = JINJA_ENVIRONMENT.get_template('templates/templateMyEvents.html')
        self.response.write(template.render(template_values))


class MostrarMisPonentes(webapp2.RequestHandler):
    def get(self):
        ponentes = controladorPonente.listarPonentes(self)
        template_values = {'ponentes': ponentes}
        template = JINJA_ENVIRONMENT.get_template('templates/templatePonentes.html')
        self.response.write(template.render(template_values))


class MostrarError(webapp2.RequestHandler):
    """
    Es llamada por /miseventos
    """
    def get(self):
        """
        Muestra la página de error
        """
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/templateError.html')
        self.response.write(template.render(template_values))


class NuevoUsuario(webapp2.RequestHandler):
    """Es llamada por /registrate"""
    def get(self):
        """
        Muestra el formulario de registro de nuevo usuario
        """
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/templatesNewUser.html')
        self.response.write(template.render(template_values))

    def post(self):
        nombre = self.request.get("nombre").strip()
        apellidos = self.request.get("apellidos").strip()
        email = self.request.get("email").strip()
        telefono = self.request.get("telefono").strip()
        twitter = self.request.get("twitter").strip()
        web = self.request.get("web").strip()
        password = self.request.get("contrasena").strip()
        idNuevoUsuario = controladorUsuario.nuevoRegistroUsuario(
            nombre, apellidos,
            email, telefono,
            twitter, web,
            password)
        self.redirect('/')


class Login(webapp2.RequestHandler):
    """ Es llamada por /login"""

    def get(self):
        """
        Muestra el formulario de login
        """
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('templates/templateLogin.html')
        self.response.write(template.render(template_values))

    def post(self):
        """
        Recibe el usuario y contraseña y comprueba que el login es correcto
        Si lo es, añade las cookies y queda iniciada la sesión
        """
        contrasena = self.request.get("contrasena").strip()
        logeado = controladorUsuario.loginCorrecto(self.request.get("email").strip(), contrasena)

        if logeado is not False:
            logeado = logeado.get()
            self.response.headers.add_header('Set-Cookie', "logged=true")
            self.response.headers.add_header('Set-Cookie', "email=" + str(logeado.email))
            self.response.headers.add_header('Set-Cookie', "key=" + str(logeado.key.id()))
            self.redirect("/")
        else:
            self.redirect("/login")


class Logout(webapp2.RequestHandler):
    """Es llamada por /logout"""

    def get(self):
        """
        Elimina las cookies relacionadas y queda cerrada la sesión
        """
        if self.request.cookies.get("logged") == "true":
            self.response.headers.add_header('Set-Cookie', "logged=; Expires=Thu, 01-Jan-1970 00:00:00 GMT")
            self.response.headers.add_header('Set-Cookie', "email=; Expires=Thu, 01-Jan-1970 00:00:00 GMT")
            self.response.headers.add_header('Set-Cookie', "key=; Expires=Thu, 01-Jan-1970 00:00:00 GMT")

        self.redirect("/")


class EliminarEvento(webapp2.RequestHandler):
    """Es llamada por /eliminarEvento"""

    def post(self):
        """
        Recibe el id del evento a borrar por post, y lo borra de la BD
        """
        user = controladorUsuario.getUsuarioLogeado(self)
        idEvento = self.request.get('id')
        if user is False:
            self.redirect("/")
        else:
            ret = controladorEvento.DeleteEvento(idEvento)
            resp = {'response': ret}
            self.response.headers['Content-Type'] = 'application/json'
            self.response.write(json.dumps(resp))

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/iEvento', InsertarEvento),
    ('/iPonente', InsertarPonente),
    ('/miseventos', MostrarMisEventos),
    ('/eventos*', MostrarEvento),
    ('/misponentes', MostrarMisPonentes),
    ('/misinformes', MostrarInforme),
    ('/micuenta', MostrarMiCuenta),
    ('/registrate', NuevoUsuario),
    ('/login', Login),
    ('/logout', Logout),
    ('/eliminarEvento', EliminarEvento),
    ('/error', MostrarError)
], debug=True)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

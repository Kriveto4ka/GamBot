"""Handlers package for GameTODO Bot."""
from aiogram import Router
from bot.handlers.start import start_router
from bot.handlers.menu import menu_router
from bot.handlers.task_create import task_create_router
from bot.handlers.task_list import task_list_router

__all__ = ["start_router", "menu_router", "task_create_router", "task_list_router"]

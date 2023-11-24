# General Imports
import argparse
from typing import Callable

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable, Status
from consumptionbackend.Personnel import Personnel
from consumptionbackend.Series import Series
from .SubNamespaceAction import SubNamespaceAction
from .CLIHandling import CLIHandler, PersonnelHandler, ConsumableHandler, SeriesHandler


def get_main_parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(
        prog="Consumption CLI", description="A CLI tool for tracking media consumption")
    sub_parsers = main_parser.add_subparsers()
    main_parser.set_defaults(handler=CLIHandler, mode="none")
    # Consumable
    add_consumable_parsers(sub_parsers)
    # Personnel
    add_personnel_parsers(sub_parsers)
    # Series
    add_series_parsers(sub_parsers)
    return main_parser


def add_where_set(parser: argparse.ArgumentParser, id: Callable, args: Callable) -> None:
    sub = parser.add_subparsers()
    where_parser = sub.add_parser("where", aliases=["w"])
    id(where_parser, "where")
    args(where_parser, "where")
    where_sub = where_parser.add_subparsers()
    set_parser = where_sub.add_parser("set", aliases=["s"])
    args(set_parser, "set")

# Consumable Parsing


def add_consumable_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    cons_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "consumable", aliases=["c"], help="action on consumable entities")
    cons_parser.set_defaults(handler=ConsumableHandler)
    cons_parser.add_argument("--df", "--dateformat", dest="date_format", default=r"%Y/%m/%d",
                             metavar="FORMAT", help="date format string, e.g %%Y/%%m/%%d")
    sub_cons_parsers = cons_parser.add_subparsers()
    # New Consumable
    cons_parser_new = sub_cons_parsers.add_parser(
        "new", aliases=["n"], help="create a new consumable")
    cons_parser_new.set_defaults(mode="new")
    add_consumable_arguments(cons_parser_new, "new")
    # List Consumable
    cons_parser_list = sub_cons_parsers.add_parser(
        "list", aliases=["l"], help="list consumables")
    cons_parser_list.set_defaults(mode="list")
    cons_parser_list.add_argument("-o", "--order", dest="order",
                                  choices=ConsumableHandler.ORDER_LIST, default="name", help="order by attribute")
    cons_parser_list.add_argument(
        "--rv", "--reverse", dest="reverse", action="store_true", help="reverse order of listing")
    add_consumable_id_arg(cons_parser_list, "where")
    add_consumable_arguments(cons_parser_list, "where")
    # Update Consumable
    cons_parser_update = sub_cons_parsers.add_parser(
        "update", aliases=["u"], help="update existing consumable")
    cons_parser_update.set_defaults(mode="update")
    add_where_set(cons_parser_update, add_consumable_id_arg,
                  add_consumable_arguments)
    # Delete Consumable
    cons_parser_delete = sub_cons_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing consumable")
    cons_parser_delete.set_defaults(mode="delete")
    add_consumable_id_arg(cons_parser_delete, "where")
    add_consumable_arguments(cons_parser_delete, "where")


def add_consumable_id_arg(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("-i", "--id", type=int,
                        dest=f"{dest}.id", action=SubNamespaceAction, default=argparse.SUPPRESS, help="unique consumable id")


def add_consumable_arguments(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("--sid", "--seriesid", type=int,
                        dest=f"{dest}.series_id", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="SERIES_ID", help="unique series id")
    parser.add_argument("-n", "--name", dest=f"{dest}.name", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="NAME", help="consumable name")
    parser.add_argument("-t", "--type", type=str.upper, dest=f"{dest}.type", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="TYPE", help="type of consumable, e.g. Novel, Movie")
    parser.add_argument("-s", "--status", dest=f"{dest}.status", choices=[
                        e.name for e in Status], action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="STATUS", help="progress status")
    parser.add_argument("-p", "--parts", type=int, dest=f"{dest}.parts", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="PART", help="e.g. Chapter, Episode")
    parser.add_argument("-c", "--completions", type=int, dest=f"{dest}.completions",
                        action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="COMPLETIONS", help="times completed")
    parser.add_argument("-r", "--rating", type=float, dest=f"{dest}.rating", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="RATING", help="numerical score")
    parser.add_argument("--sd", "--startdate", dest=f"{dest}.start_date", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="DATE", help="date of initial start")
    parser.add_argument("--ed", "--enddate", dest=f"{dest}.end_date", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="DATE", help="date of first completion")


# Series Parsing


def add_series_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    series_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "series", aliases=["s"], help="action on series entities")
    series_parser.set_defaults(handler=SeriesHandler)
    sub_series_parsers = series_parser.add_subparsers()
    # New Series
    series_parser_new = sub_series_parsers.add_parser(
        "new", aliases=["n"], help="create a new series")
    series_parser_new.set_defaults(mode="new")
    add_series_arguments(series_parser_new, "new")
    # List Series
    series_parser_list = sub_series_parsers.add_parser(
        "list", aliases=["l"], help="list series")
    series_parser_list.set_defaults(mode="list")
    series_parser_list.add_argument("-o", "--order", dest="order",
                                    choices=SeriesHandler.ORDER_LIST, default="name", help="order by attribute")
    series_parser_list.add_argument(
        "--rv", "--reverse", dest="reverse", action="store_true", help="reverse order of listing")
    add_series_id_arg(series_parser_list, "where")
    add_series_arguments(series_parser_list, "where")
    # Update Series
    series_parser_update = sub_series_parsers.add_parser(
        "update", aliases=["u"], help="update existing series")
    series_parser_update.set_defaults(mode="update")
    add_where_set(series_parser_update,
                  add_series_id_arg, add_series_arguments)
    # Delete Series
    series_parser_delete = sub_series_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing series")
    series_parser_delete.set_defaults(mode="delete")
    add_series_id_arg(series_parser_delete, "where")
    add_series_arguments(series_parser_delete, "where")


def add_series_id_arg(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("-i", "--id", type=int,
                        dest=f"{dest}.id", action=SubNamespaceAction, default=argparse.SUPPRESS, help="unique series id")


def add_series_arguments(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("-n", "--name", dest=f"{dest}.name", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="NAME", help="series name")


# Personnel Parsing


def add_personnel_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    personnel_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "personnel", aliases=["p"], help="action on personnel entities")
    personnel_parser.set_defaults(handler=PersonnelHandler)
    sub_personnel_parsers = personnel_parser.add_subparsers()
    # New Series
    personnel_parser_new = sub_personnel_parsers.add_parser(
        "new", aliases=["n"], help="create new personnel")
    personnel_parser_new.set_defaults(mode="new")
    add_personnel_arguments(personnel_parser_new, "new")
    # List Series
    personnel_parser_list = sub_personnel_parsers.add_parser(
        "list", aliases=["l"], help="list personnel")
    personnel_parser_list.set_defaults(mode="list")
    personnel_parser_list.add_argument("-o", "--order", dest="order",
                                       choices=PersonnelHandler.ORDER_LIST, default="first_name", help="order by attribute")
    personnel_parser_list.add_argument(
        "--rv", "--reverse", dest="reverse", action="store_true", help="reverse order of listing")
    add_personnel_id_arg(personnel_parser_list, "where")
    add_personnel_arguments(personnel_parser_list, "where")
    # Update Series
    personnel_parser_update = sub_personnel_parsers.add_parser(
        "update", aliases=["u"], help="update existing personnel")
    personnel_parser_update.set_defaults(mode="update")
    add_where_set(personnel_parser_update,
                  add_personnel_id_arg, add_personnel_arguments)
    # Delete Series
    personnel_parser_delete = sub_personnel_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing personnel")
    personnel_parser_delete.set_defaults(mode="delete")
    add_personnel_id_arg(personnel_parser_delete, "where")
    add_personnel_arguments(personnel_parser_delete, "where")


def add_personnel_id_arg(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("-i", "--id", type=int,
                        dest=f"{dest}.id", action=SubNamespaceAction, default=argparse.SUPPRESS, help="unique personnel id")


def add_personnel_arguments(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument("-f", "--firstname", dest=f"{dest}.first_name", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="FIRST NAME", help="personnel first name")
    parser.add_argument("-l", "--lastname", dest=f"{dest}.last_name", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="LAST NAME", help="personnel last name")
    parser.add_argument("-p", "--pseudonym", dest=f"{dest}.pseudonym", action=SubNamespaceAction,
                        default=argparse.SUPPRESS, metavar="PSEUDONYM", help="personnel pseudonym")

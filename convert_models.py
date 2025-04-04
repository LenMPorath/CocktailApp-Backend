import os
import importlib.util
import inspect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union


def python_type_to_ts(python_type: Any) -> str:
    """Konvertiert Python-Typen in TypeScript-Typen."""
    mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        list: "any[]",
        dict: "Record<string, any>",
        None: "null",
    }

    if python_type in mapping:
        return mapping[python_type]
    elif hasattr(python_type, "__origin__"):  # Generics wie Optional[str]
        origin = python_type.__origin__
        args = python_type.__args__
        if origin is Union and len(args) == 2 and args[1] is type(None):
            return f"{python_type_to_ts(args[0])} | null"
        if origin is list:
            return f"{python_type_to_ts(args[0])}[]"
        if origin is dict:
            return f"Record<{python_type_to_ts(args[0])}, {python_type_to_ts(args[1])}>"
    return "any"


def convert_pydantic_model_to_ts(model: Any) -> str:
    """Konvertiert ein Pydantic-Modell in ein TypeScript-Interface."""
    ts_interface = f"export interface {model.__name__} {{\n"
    
    for field_name, field_info in model.model_fields.items():
        ts_type = python_type_to_ts(field_info.annotation)
        optional = "?" if not field_info.is_required() else ""
        ts_interface += f"  {field_name}{optional}: {ts_type};\n"

    ts_interface += "}\n"
    return ts_interface


def process_python_file(file_path: str, output_dir: str):
    """Lädt eine Python-Datei dynamisch und konvertiert alle Pydantic-Modelle nach TypeScript."""
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Debug-Ausgabe für den Dateipfad
    print(f"Verarbeite Datei: {file_path}")

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    ts_code = ""

    # Durchsucht alle Mitglieder und prüft auf Pydantic-Modelle
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj is not BaseModel:
            print(f"  → Pydantic Modell gefunden: {obj.__name__}")
            ts_code += convert_pydantic_model_to_ts(obj) + "\n"

    if ts_code:
        output_path = os.path.join(output_dir, module_name + ".ts")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ts_code)
        print(f"✅ {file_path} → {output_path}")
    else:
        print(f"❌ Keine Pydantic Modelle in {file_path} gefunden.")



def main():
    """Hauptfunktion zum Durchlaufen aller Schema-Dateien."""
    source_dir = "app/schemas"
    target_dir = "../CocktailApp-Frontend/src/lib/models"

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".py"):
                process_python_file(os.path.join(root, file), target_dir)


if __name__ == "__main__":
    main()

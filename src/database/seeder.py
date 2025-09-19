import pkgutil
import importlib
import inspect
from typing import List, Type, Dict, Any
from sqlalchemy.orm import Session
from .db import db_config

class BaseSeeder:
    """Base seeder class"""
    
    def __init__(self):
        self.db: Session = db_config.SessionLocal()
    
    def run(self):
        """Override this method in child classes"""
        raise NotImplementedError("Subclass must implement run method")
    
    def close(self):
        """Close database session"""
        self.db.close()

class SeederRegistry:
    """Registry to auto-discover and manage seeders"""
    
    def __init__(self):
        self._seeders: List[Type[BaseSeeder]] = []
        self._discovered = False
    
    def register(self, seeder_class: Type[BaseSeeder]):
        """Manually register a seeder class"""
        if issubclass(seeder_class, BaseSeeder) and seeder_class not in self._seeders:
            self._seeders.append(seeder_class)
    
    def discover_seeders(self, package_name: str = "src.database.seed"):
        """Auto-discover seeders from seed package"""
        if self._discovered:
            return
            
        try:
            # Import the seed package
            seed_package = importlib.import_module(package_name)
            
            # Iterate through all modules in the package
            for finder, module_name, ispkg in pkgutil.iter_modules(seed_package.__path__):
                if ispkg:
                    continue
                    
                try:
                    # Import the module
                    full_module_name = f"{package_name}.{module_name}"
                    module = importlib.import_module(full_module_name)
                    
                    # Find all seeder classes in the module
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, BaseSeeder) and 
                            obj is not BaseSeeder and 
                            obj.__module__ == full_module_name):
                            self.register(obj)
                            
                except ImportError as e:
                    print(f"⚠️ Could not import {full_module_name}: {e}")
                    
        except ImportError:
            print(f"⚠️ Could not import package {package_name}")
        
        self._discovered = True
    
    def get_seeders(self) -> List[Type[BaseSeeder]]:
        """Get all registered seeders"""
        if not self._discovered:
            self.discover_seeders()
        return self._seeders
    
    def get_seeder_by_name(self, name: str) -> Type[BaseSeeder]:
        """Get seeder by class name"""
        seeders = self.get_seeders()
        for seeder in seeders:
            if seeder.__name__ == name:
                return seeder
        raise ValueError(f"Seeder '{name}' not found")

# Global registry instance
registry = SeederRegistry()

def run_all_seeders():
    """Run all discovered seeders"""
    seeders = registry.get_seeders()
    
    if not seeders:
        print("⚠️ No seeders found")
        return
    
    print("🌱 Starting database seeding...")
    
    for SeederClass in seeders:
        try:
            print(f"🌱 Running {SeederClass.__name__}...")
            seeder = SeederClass()
            seeder.run()
            seeder.close()
            print(f"✅ {SeederClass.__name__} completed")
        except Exception as e:
            print(f"❌ Seeder {SeederClass.__name__} failed: {e}")
            try:
                seeder.close()
            except:
                pass
    
    print("✅ Database seeding completed")

def run_seeder(seeder_name: str):
    """Run specific seeder by name"""
    try:
        SeederClass = registry.get_seeder_by_name(seeder_name)
        
        print(f"🌱 Running {seeder_name}...")
        seeder = SeederClass()
        seeder.run()
        seeder.close()
        print(f"✅ {seeder_name} completed")
        
    except ValueError as e:
        print(f"❌ {e}")
        available = [s.__name__ for s in registry.get_seeders()]
        print(f"Available seeders: {available}")
    except Exception as e:
        print(f"❌ {seeder_name} failed: {e}")

def list_seeders():
    """List all available seeders"""
    seeders = registry.get_seeders()
    print("\n📋 Available Seeders:")
    print("=" * 30)
    for seeder in seeders:
        print(f"• {seeder.__name__}")
        if seeder.__doc__:
            print(f"  {seeder.__doc__.strip()}")
    print("=" * 30)

# Backward compatibility - keep the old SEEDERS list but populate from registry
def get_legacy_seeders():
    """Get seeders in legacy format for backward compatibility"""
    return registry.get_seeders()

# Simply use a global variable for backward compatibility
SEEDERS = get_legacy_seeders()
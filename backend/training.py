from pathlib import Path
import zipfile
import shutil
import threading
import uuid
import yaml

from ultralytics import YOLO


# =========================================================
# Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

AI_DIR = BASE_DIR / "ai"

MODEL_PATH = (
    AI_DIR
    / "models"
    / "yolo11n.pt"
)

TRAINING_DIR = (
    AI_DIR
    / "training"
)

DATASET_DIR = (
    TRAINING_DIR
    / "dataset"
)

RUNS_DIR = (
    TRAINING_DIR
    / "runs"
)

MODELS_DIR = (
    AI_DIR
    / "models"
)


# =========================================================
# Create directories
# =========================================================

TRAINING_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RUNS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MODELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# Training state
# =========================================================

training_state = {
    "status": "idle",
    "job_id": None,
    "progress": 0,
    "epoch": 0,
    "total_epochs": 0,
    "message": "No training started",
    "model": None,
    "best_model": None,
    "error": None
}


# =========================================================
# Get training status
# =========================================================

def get_training_status():

    return training_state.copy()


# =========================================================
# Safely extract ZIP
# =========================================================

def safe_extract_zip(
    zip_path: str,
    destination: Path
):

    destination = destination.resolve()

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_ref:

        for member in zip_ref.infolist():

            member_path = (
                destination
                / member.filename
            ).resolve()

            if not str(member_path).startswith(
                str(destination)
            ):

                raise RuntimeError(
                    "Unsafe ZIP file detected."
                )

        zip_ref.extractall(
            destination
        )


# =========================================================
# Find data.yaml
# =========================================================

def find_data_yaml(
    dataset_dir: Path
):

    yaml_files = []

    for path in dataset_dir.rglob("*"):

        if (
            path.is_file()
            and path.name.lower() == "data.yaml"
        ):

            yaml_files.append(path)

    if not yaml_files:

        raise RuntimeError(
            "data.yaml was not found in the downloaded dataset."
        )

    return yaml_files[0]


# =========================================================
# Resolve dataset path
# =========================================================

def resolve_dataset_path(
    yaml_path,
    dataset_root: Path
):

    value = Path(
        str(yaml_path)
    )

    # Absolute path

    if value.is_absolute():

        if value.exists():

            return value

        # If the absolute path belongs to the
        # original Roboflow environment, use
        # the path relative to its final component.

        value_parts = value.parts

        for index, part in enumerate(
            value_parts
        ):

            if part.lower() in {
                "train",
                "valid",
                "val",
                "test"
            }:

                relative_path = Path(
                    *value_parts[index:]
                )

                candidate = (
                    dataset_root
                    / relative_path
                )

                if candidate.exists():

                    return candidate

        return value

    # Relative path

    candidate = (
        dataset_root
        / value
    ).resolve()

    if candidate.exists():

        return candidate

    # Try directly from dataset directory

    candidate = (
        DATASET_DIR
        / value
    ).resolve()

    if candidate.exists():

        return candidate

    return (
        dataset_root
        / value
    ).resolve()


# =========================================================
# Find images directory
# =========================================================

def find_images_directory(
    dataset_dir: Path,
    split: str
):

    possible_names = []

    if split == "valid":

        possible_names = [
            "valid/images",
            "val/images"
        ]

    elif split == "val":

        possible_names = [
            "val/images",
            "valid/images"
        ]

    else:

        possible_names = [
            f"{split}/images"
        ]

    # First try known structures

    for relative in possible_names:

        candidate = (
            dataset_dir
            / relative
        )

        if candidate.exists():

            return candidate

    # Fallback: search recursively

    for path in dataset_dir.rglob("images"):

        if not path.is_dir():

            continue

        parent_name = (
            path.parent.name.lower()
        )

        if parent_name == split.lower():

            return path

    return None


# =========================================================
# Count images
# =========================================================

def count_images(
    directory: Path
):

    if directory is None:

        return 0

    extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp"
    }

    return sum(
        1
        for path in directory.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in extensions
        )
    )


# =========================================================
# Prepare dataset
# =========================================================

def prepare_dataset(
    zip_path: str
):

    global training_state

    # -----------------------------------------------------
    # Clean previous extracted dataset
    # -----------------------------------------------------

    if DATASET_DIR.exists():

        shutil.rmtree(
            DATASET_DIR
        )

    DATASET_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    training_state["message"] = (
        "Extracting dataset..."
    )

    # -----------------------------------------------------
    # Validate ZIP before extraction
    # -----------------------------------------------------

    if not Path(zip_path).exists():

        raise RuntimeError(
            f"Dataset ZIP does not exist: {zip_path}"
        )

    if not zipfile.is_zipfile(zip_path):

        raise RuntimeError(
            "Downloaded dataset is not a valid ZIP file."
        )

    # -----------------------------------------------------
    # Extract
    # -----------------------------------------------------

    safe_extract_zip(
        zip_path,
        DATASET_DIR
    )

    # -----------------------------------------------------
    # Find data.yaml
    # -----------------------------------------------------

    training_state["message"] = (
        "Searching for data.yaml..."
    )

    data_yaml_path = find_data_yaml(
        DATASET_DIR
    )

    # -----------------------------------------------------
    # Read YAML
    # -----------------------------------------------------

    with open(
        data_yaml_path,
        "r",
        encoding="utf-8"
    ) as file:

        data_config = yaml.safe_load(
            file
        )

    if not isinstance(
        data_config,
        dict
    ):

        raise RuntimeError(
            "Invalid data.yaml format."
        )

    # -----------------------------------------------------
    # Determine dataset root
    # -----------------------------------------------------

    dataset_root = (
        data_yaml_path.parent
    )

    yaml_root = data_config.get(
        "path"
    )

    if yaml_root:

        yaml_root_path = Path(
            str(yaml_root)
        )

        if yaml_root_path.is_absolute():

            if yaml_root_path.exists():

                dataset_root = (
                    yaml_root_path
                )

        else:

            candidate = (
                data_yaml_path.parent
                / yaml_root_path
            ).resolve()

            if candidate.exists():

                dataset_root = candidate

    # -----------------------------------------------------
    # Class names
    # -----------------------------------------------------

    names = data_config.get(
        "names"
    )

    if names is None:

        raise RuntimeError(
            "No 'names' field found in data.yaml."
        )

    # -----------------------------------------------------
    # Required paths
    # -----------------------------------------------------

    train_path = data_config.get(
        "train"
    )

    val_path = data_config.get(
        "val"
    )

    test_path = data_config.get(
        "test"
    )

    if not train_path:

        raise RuntimeError(
            "Training path is missing from data.yaml."
        )

    if not val_path:

        raise RuntimeError(
            "Validation path is missing from data.yaml."
        )

    # -----------------------------------------------------
    # Resolve paths
    # -----------------------------------------------------

    train_dir = resolve_dataset_path(
        train_path,
        dataset_root
    )

    val_dir = resolve_dataset_path(
        val_path,
        dataset_root
    )

    test_dir = None

    if test_path:

        test_dir = resolve_dataset_path(
            test_path,
            dataset_root
        )

    # -----------------------------------------------------
    # If YAML paths point directly to images
    # directories, use them.
    #
    # Otherwise locate the split directories.
    # -----------------------------------------------------

    if not train_dir.exists():

        train_images = find_images_directory(
            DATASET_DIR,
            "train"
        )

        if train_images:

            train_dir = train_images

    if not val_dir.exists():

        val_images = find_images_directory(
            DATASET_DIR,
            "valid"
        )

        if not val_images:

            val_images = find_images_directory(
                DATASET_DIR,
                "val"
            )

        if val_images:

            val_dir = val_images

    if test_path and not test_dir.exists():

        test_images = find_images_directory(
            DATASET_DIR,
            "test"
        )

        if test_images:

            test_dir = test_images

    # -----------------------------------------------------
    # Validate directories
    # -----------------------------------------------------

    train_count = count_images(
        train_dir
    )

    val_count = count_images(
        val_dir
    )

    test_count = count_images(
        test_dir
    )

    if not train_dir.exists():

        raise RuntimeError(
            "Training images directory was not found."
        )

    if not val_dir.exists():

        raise RuntimeError(
            "Validation images directory was not found."
        )

    if train_count == 0:

        raise RuntimeError(
            "Training images directory is empty."
        )

    if val_count == 0:

        raise RuntimeError(
            "Validation images directory is empty."
        )

    # -----------------------------------------------------
    # Build a clean data.yaml using actual local paths
    # -----------------------------------------------------

    prepared_yaml = (
        TRAINING_DIR
        / "data.yaml"
    )

    prepared_config = {
        "path": str(
            DATASET_DIR.resolve()
        ),
        "train": str(
            train_dir.resolve()
        ),
        "val": str(
            val_dir.resolve()
        ),
        "names": names
    }

    if test_dir and test_dir.exists():

        prepared_config["test"] = str(
            test_dir.resolve()
        )

    with open(
        prepared_yaml,
        "w",
        encoding="utf-8"
    ) as file:

        yaml.safe_dump(
            prepared_config,
            file,
            sort_keys=False
        )

    # -----------------------------------------------------
    # Report dataset information
    # -----------------------------------------------------

    training_state["message"] = (
        f"Dataset ready: "
        f"{train_count} training images, "
        f"{val_count} validation images."
    )

    return {

        "yaml":
            prepared_yaml,

        "names":
            names,

        "train":
            train_dir,

        "val":
            val_dir,

        "test":
            test_dir,

        "train_images":
            train_count,

        "validation_images":
            val_count,

        "test_images":
            test_count
    }


# =========================================================
# Training callback
# =========================================================

def on_train_epoch_end(
    trainer
):

    global training_state

    epoch = (
        trainer.epoch + 1
    )

    total_epochs = (
        trainer.epochs
    )

    progress = int(
        (epoch / total_epochs)
        * 100
    )

    training_state["epoch"] = (
        epoch
    )

    training_state["total_epochs"] = (
        total_epochs
    )

    training_state["progress"] = (
        progress
    )

    training_state["message"] = (
        f"Training epoch "
        f"{epoch}/{total_epochs}"
    )


# =========================================================
# Train model
# =========================================================

def train_model(
    zip_path: str,
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 8
):

    global training_state

    try:

        # -------------------------------------------------
        # Generate job ID
        # -------------------------------------------------

        job_id = str(
            uuid.uuid4()
        )

        training_state.update({

            "status":
                "preparing",

            "job_id":
                job_id,

            "progress":
                0,

            "epoch":
                0,

            "total_epochs":
                epochs,

            "message":
                "Preparing dataset...",

            "model":
                "YOLO11n",

            "best_model":
                None,

            "error":
                None
        })

        # -------------------------------------------------
        # Prepare dataset
        # -------------------------------------------------

        prepared = prepare_dataset(
            zip_path
        )

        # -------------------------------------------------
        # Load model
        # -------------------------------------------------

        training_state["status"] = (
            "loading_model"
        )

        training_state["message"] = (
            "Loading YOLO11n model..."
        )

        model = YOLO(
            str(MODEL_PATH)
        )

        # -------------------------------------------------
        # Register callback
        # -------------------------------------------------

        model.add_callback(
            "on_train_epoch_end",
            on_train_epoch_end
        )

        # -------------------------------------------------
        # Start training
        # -------------------------------------------------

        training_state["status"] = (
            "training"
        )

        training_state["message"] = (
            "YOLO11 training started."
        )

        model.train(

            data=str(
                prepared["yaml"]
            ),

            epochs=epochs,

            imgsz=imgsz,

            batch=batch,

            project=str(
                RUNS_DIR
            ),

            name=job_id,

            exist_ok=True,

            pretrained=True,

            verbose=True
        )

        # -------------------------------------------------
        # Locate best model
        # -------------------------------------------------

        run_dir = (
            RUNS_DIR
            / job_id
        )

        best_model = (
            run_dir
            / "weights"
            / "best.pt"
        )

        # -------------------------------------------------
        # Copy final model
        # -------------------------------------------------

        final_model = (
            MODELS_DIR
            / "pilotwatch_best.pt"
        )

        if best_model.exists():

            shutil.copy2(
                best_model,
                final_model
            )

        else:

            raise RuntimeError(
                "Training finished but best.pt "
                "was not created."
            )

        # -------------------------------------------------
        # Complete
        # -------------------------------------------------

        training_state.update({

            "status":
                "completed",

            "progress":
                100,

            "epoch":
                epochs,

            "total_epochs":
                epochs,

            "message":
                "Model training completed.",

            "best_model":
                str(
                    final_model
                ),

            "error":
                None
        })

    except Exception as e:

        training_state.update({

            "status":
                "failed",

            "message":
                "Training failed.",

            "error":
                str(e)
        })


# =========================================================
# Start training in background
# =========================================================

def start_training(
    zip_path: str,
    epochs: int = 50,
    imgsz: int = 640,
    batch: int = 8
):

    if training_state["status"] in {

        "preparing",

        "loading_model",

        "training"

    }:

        raise RuntimeError(
            "Training is already running."
        )

    thread = threading.Thread(

        target=train_model,

        args=(

            zip_path,

            epochs,

            imgsz,

            batch

        ),

        daemon=True
    )

    thread.start()

    return training_state.copy()
from .trainer import CurriculumTrainer
from .validation import robust_validation, validate_on_date
from .loss import curriculum_loss
from .backtesting import historical_backtesting


# Attach methods to CurriculumTrainer class
CurriculumTrainer.historical_backtesting = historical_backtesting
CurriculumTrainer.curriculum_loss = curriculum_loss
CurriculumTrainer.robust_validation = robust_validation
CurriculumTrainer.validate_on_date = validate_on_date

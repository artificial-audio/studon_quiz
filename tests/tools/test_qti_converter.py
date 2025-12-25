# from qti_package_maker.package_interface import QTIPackageInterface

# def example():
#     # Initialize the package with a name
#     qti_packer = QTIPackageInterface("example_assessment", verbose=True)

#     # Add a multiple-choice question
#     qti_packer.add_item("MC", (
# 	    "What is your favorite color?",
# 	    ["blue", "red", "yellow"],
# 	    "blue",
#     ))

#     # # Add a multiple-answer question
#     # qti_packer.add_item("MA", (
#     # 	"Which of these are fruits?",
#     # 	["apple", "carrot", "banana", "broccoli"],
#     # 	["apple", "banana"],
#     # ))


#     # Save as Canvas QTI v1.2
#     qti_packer.save_package("canvas_qti_v1_2")

#     # Save as Blackboard QTI v2.1
#     qti_packer.save_package("blackboard_qti_v2_1")

class QtiConverter:
    pass
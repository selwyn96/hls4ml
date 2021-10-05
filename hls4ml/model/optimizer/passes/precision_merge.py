from hls4ml.model.optimizer import OptimizerPass
from hls4ml.model.hls_model import FixedPrecisionType

class SetPrecisionConcat(OptimizerPass):
    def match(self, node):
        if node.__class__.__name__ == 'Concatenate':
            otype = node.get_output_variable().type.precision
            itype1 = node.get_input_variable(node.inputs[0]).type.precision
            itype2 = node.get_input_variable(node.inputs[1]).type.precision
            print('SetPrecisionConcat')
            print(otype, itype1, itype2)
            if isinstance(otype, FixedPrecisionType) \
               and (otype.width < max(itype1.width, itype2.width) or \
                    otype.integer < max(itype1.integer, itype2.integer)):
                return True
        return False
    
    def transform(self, model, node):
        """
        Set merge output precision
        """
        print("Found {} in the model, optimizing ...".format(node.name))
        otype = node.get_output_variable().type.precision
        itype1 = node.get_input_variable(node.inputs[0]).type.precision
        itype2 = node.get_input_variable(node.inputs[1]).type.precision

        newtype = FixedPrecisionType(max(itype1.width, itype2.width), max(itype1.integer, itype2.integer), otype.signed, 
                                     otype.rounding_mode, ostype.saturation_mode, otype.saturation_bits)
        node.get_output_variable().type.precision = newtype
       
        return True

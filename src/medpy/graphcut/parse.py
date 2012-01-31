"""
@package medpy.graphcut.parse
Parses the output returned by graph-cut implementations.

When the cut module of this package has been used or a manual execution of the supported
graph-cut algorithms has been undertaken, the functionalities provided by this module can
be used to parse the results and apply it to the original images. 

All functions in this module are highly depend on the actual implementation of the
graph-cut algorithm they are intended to be used for. They require a minimal version
number and it can not be ensured, that they will work with other versions.

See the package description for a list of the supported graph-cut implementations.

Functions:
    - def bk_mfmc_parse(output): Parse the output of Boyov and Kolmogorovs max-flow/min-cut algorithm.

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in modules

# third-party modules
import scipy

# own modules
from ..core.Logger import Logger
from ..core.exceptions import ArgumentError
from .generate import __BK_MFMC_SOURCE_MARKER, __BK_MFMC_SINK_MARKER

#####
# General functions
#####
def apply_mapping(label_image, mapping):
    """
    Apply a region-to-source/sink mapping to a label image.
    
    Takes the original label image and a mapping from its region ids to source/sink as
    returned by one of this modules *_parse functions. From this a binary mask is created
    where True values denote source and False sink affiliation for each voxel.
    
    @param label_image: A nD label_image
    @type label_image: sequence
    @param mapping: A mapping of the label_images region ids to source or sink.
    @type mapping: dict
    
    @return: A binary image
    @rtype: numpy.ndarray
    
    @raise ArgumentError: If a region id is missing in the supplied mapping
    """
    label_image = scipy.array(label_image)
    rav = label_image.ravel()
    for i in range(len(rav)):
        if not rav[i] in mapping:
            raise ArgumentError('No conversion for region id {} found in the supplied mapping.'.format(rav[i]))
        rav[i] = mapping[rav[i]]
    return rav.reshape(label_image.shape).astype(scipy.bool_)
    

#####
# BK_MFMC: Boyov and Kolmogorovs (1) C++ max-flow/min-cut implementation (a)
#####

def bk_mfmc_parse(output):
    """
    Parse the output generated by a Boyov and Kolmogorovs max-flow/min-cut algorithm
    execution.
    
    The result maps from the region-ids of the original image to either source or sink.
    
    The original source file has to be generated using @link: bk_mfmc_generate() to
    ensure correct parsing.
    
    @param output: The output returned by @link: bk_mfmc_cut() or a manual execution.
    @type output: str
    @return: (maxflow, map) where maxflow is and int and map a dictionary containing
             node_id->BK_MFMC_SOURCE_MARKER / BK_MFMC_SINK_MARKER ({node_id: source|sink, ...})
             mappings (@link: graph.BK_MFMC_SOURCE_MARKER, @link: graph.BK_MFMC_SINK_MARKER).
    @rtype: dict
    
    @raise ArgumentError: When the supplied output is maleformed.
    """
    # prepare logger
    logger = Logger.getInstance()
    
    logger.info('Parsing results...')
    try:
        lines = output.split('\n')
        flow = int(lines[0][lines[0].find('=') + 1:])
        nodes = {}
        for line in lines[1:]:
            line = line.strip()
            if 0 == len(line) or '#' == line[0]: continue # skip comments and empty lines
            nodes[int(line[:line.find('=')])] = int(line[line.find('=') + 1:])
        logger.debug('flow={}, #nodes={}, #source={}, #sink={}'.format(flow, 
                                                                       len(nodes), 
                                                                       sum([1 if x == __BK_MFMC_SOURCE_MARKER else 0 for x in nodes.values()]),
                                                                       sum([1 if x == __BK_MFMC_SINK_MARKER else 0 for x in nodes.values()])))
        return (flow, nodes)
    except ValueError as e:
        raise ArgumentError('Maleformed results argument: {}.'.format(e.message), e)
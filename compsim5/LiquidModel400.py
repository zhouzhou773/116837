from pypcsimplus import * 
import pypcsimplus as pcsim

class LiquidModel400(pcsim.Model):
    
    
    def defaultParameters(self):
        p = self.params
        
        p.Frac_EXC = 0.8     # fraction of excitatory neurons        
        
        p.OUScale = 0.4
        
        p.Xdim = 15
        p.Ydim = 6
        p.Zdim = 6  
                
        # weight scaling parameters        
        p.WExcScale = 1.0 
        p.WInhScale = 2.0
        
        # neuron parameters
        p.Rm = 1e8
        p.Cm = 3e-10
        p.Vthresh=-59e-3
        p.Vresting=-70e-3
        p.Vreset=-70e-3
        p.TrefractExc = 5e-3
        p.TrefractInh = 5e-3
        p.Vinit=-65e-3
        p.VinitReal = -70e-3        
        p.Inoise = 0e-10
        p.Iinject = 0e-10     
        
        # other synapse parameters
        p.synTauExc = 5e-3
        p.synDelay = 1e-3     
        p.Delay_Heter = 0.0
        p.ErevExc = 0e-3
        p.ErevInh = -75e-3
        
        
        # Dynamic Synapse parameters
        p.createNodes([ 'EE', 'EI', 'IE', 'II' ])
        
        
        p.EE.U = 0.5
        p.EE.D = 1.1
        p.EE.F = 0.02
        p.EE.delay = 1e-3
        
        p.EI.U = 0.25
        p.EI.D = 0.7
        p.EI.F = 0.02        
        
        p.IE.U = 0.05
        p.IE.D = 0.125
        p.IE.F = 1.2
        
        p.II.U = 0.32
        p.II.D = 0.144
        p.II.F = 0.06
        
        p.UDF_Heter = 0.5
        
        p.EE.Wscale = 3.3        
        p.EI.Wscale = 3.3        
        p.IE.Wscale = 3.3                
        p.II.Wscale = 3.3
        
        p.Wscale = 0.03
                
        p.W_Heter = 0.0
        
        p.d_lambda = 2.5
        
        p.EE.C = 0.1
        p.EI.C = 0.1
        p.IE.C = 0.1
        p.II.C = 0.1
        
            
    def derivedParameters(self):
        m = self.elements
        ep = self.expParams
        p = self.params
        net = self.net
        
        p.synTauInh = p.synTauExc
        
        tau_m = p.Cm * p.Rm
        tau_s = p.synTauExc
        p.EE.W = ((p.Vthresh - p.Vinit) * p.EE.Wscale * p.Wscale)/ ((p.ErevExc - p.Vinit) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))        
        p.EI.W = ((p.Vthresh - p.Vinit) * p.EI.Wscale * p.Wscale)/ ((p.ErevExc - p.Vinit) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
        
        
        tau_s = p.synTauInh    
        p.IE.W = ((p.Vthresh - p.Vinit) * p.IE.Wscale * p.Wscale)/ ((p.Vinit - p.ErevInh) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
        p.II.W = ((p.Vthresh - p.Vinit) * p.II.Wscale * p.Wscale)/ ((p.Vinit - p.ErevInh) * p.Rm * tau_s / (tau_m - tau_s) *  ((tau_s / tau_m) ** (tau_s / (tau_m - tau_s)) - (tau_s / tau_m) ** (tau_m / (tau_m - tau_s))))
        
        print "EE.W = ", p.EE.W, "EI.W =", p.EI.W, "IE.W = ", p.IE.W, "II.W = ", p.II.W 
        
        
        pass
    
    def getParameters(self):
        return self.params
    
    def generate(self):
        m = self.elements
        net = self.net
        p = self.params
        self.derivedParameters() 
        
        exc_nrn_factory = CbLifNeuron( Cm = p.Cm, 
                                       Rm = p.Rm,
                                       Vthresh=p.Vthresh, 
                                       Vresting=p.Vresting, 
                                       Vreset=p.Vreset, 
                                       Trefract=p.TrefractExc, 
                                       Vinit=p.VinitReal, 
                                       Inoise = p.Inoise, 
                                       Iinject = p.Iinject)
        
        inh_nrn_factory = CbLifNeuron( Cm = p.Cm, 
                                       Rm = p.Rm,
                                       Vthresh=p.Vthresh, 
                                       Vresting=p.Vresting, 
                                       Vreset=p.Vreset, 
                                       Trefract=p.TrefractInh, 
                                       Vinit=p.VinitReal, 
                                       Inoise = p.Inoise, 
                                       Iinject = p.Iinject)
        
        
        
        m.all_nrn_popul = SpatialFamilyPopulation( net, [ exc_nrn_factory, inh_nrn_factory ], 
                                                    RatioBasedFamilies( [4, 1]  ), 
                                                    CuboidIntegerGrid3D( p.Xdim, p.Ydim, p.Zdim ) );
                                                    
        
        
        
        m.exc_nrn_popul, m.inh_nrn_popul = tuple( m.all_nrn_popul.splitFamilies() );
        
        p.nExcNeurons = m.exc_nrn_popul.size()
        p.nInhNeurons = m.inh_nrn_popul.size()
        
        net.mount(OUNoiseSynapse(0.012e-6 * p.OUScale, 0.003e-6 * p.OUScale, 2.7e-3, 0.0), m.all_nrn_popul.idVector())
        net.mount(OUNoiseSynapse(0.057e-6 * p.OUScale, 0.0066e-6 * p.OUScale, 10.5e-3,-75e-3), m.all_nrn_popul.idVector())
        
        
        m.createNodes(["EE", "EI", "IE", "II"])
        
        EE, EI, IE, II = 0,1,2,3
        
        syn_factory = [EE, EI, IE, II]
        
        
        syn_factory[EE] = SimObjectVariationFactory( DynamicCondExpSynapse( W = p.EE.W, tau=p.synTauExc, delay= p.EE.delay ) )
        
        syn_factory[EE].set("W", BndGammaDistribution(p.EE.W, p.W_Heter, 2 * p.IE.W ))
        syn_factory[EE].set("U", BndNormalDistribution(p.EE.U, p.UDF_Heter, 0.05, 0.95))
        syn_factory[EE].set("D", BndNormalDistribution(p.EE.D, p.UDF_Heter, 5e-3, 5))
        syn_factory[EE].set("F", BndNormalDistribution(p.EE.F, p.UDF_Heter, 5e-3, 5))    
        
                
        syn_factory[EI] = SimObjectVariationFactory( DynamicCondExpSynapse( W = p.EI.W, tau=p.synTauExc, delay = p.synDelay ) )
        
        syn_factory[EI].set("W", BndGammaDistribution(p.EI.W, p.W_Heter, 2 * p.IE.W ))
        syn_factory[EI].set("U", BndNormalDistribution(p.EI.U, p.UDF_Heter, 0.05, 0.95))
        syn_factory[EI].set("D", BndNormalDistribution(p.EI.D, p.UDF_Heter, 5e-3, 5))
        syn_factory[EI].set("F", BndNormalDistribution(p.EI.F, p.UDF_Heter, 5e-3, 5))
        
        syn_factory[IE] = SimObjectVariationFactory( DynamicCondExpSynapse( W = p.IE.W, tau = p.synTauInh, delay = p.synDelay ) )
        
        syn_factory[IE].set("W", BndGammaDistribution(p.IE.W, p.W_Heter, 2 * p.IE.W ))
        syn_factory[IE].set("U", BndNormalDistribution(p.IE.U, p.UDF_Heter, 0.05, 0.95))
        syn_factory[IE].set("D", BndNormalDistribution(p.IE.D, p.UDF_Heter, 5e-3, 5))
        syn_factory[IE].set("F", BndNormalDistribution(p.IE.F, p.UDF_Heter, 5e-3, 5))
        
        
        syn_factory[II] = SimObjectVariationFactory( DynamicCondExpSynapse( W = p.II.W, tau = p.synTauInh, delay = p.synDelay ) )
        
        syn_factory[II].set("W", BndGammaDistribution(p.II.W, p.W_Heter, 2 * p.II.W ))
        syn_factory[II].set("U", BndNormalDistribution(p.II.U, p.UDF_Heter, 0.05, 0.95))
        syn_factory[II].set("D", BndNormalDistribution(p.II.D, p.UDF_Heter, 5e-3, 5))
        syn_factory[II].set("F", BndNormalDistribution(p.II.F, p.UDF_Heter, 5e-3, 5))
        
        
        m.EE.proj = ConnectionsProjection( m.exc_nrn_popul, m.exc_nrn_popul,
                                           syn_factory[EE],
                                           RandomConnections( p.EE.C ),
                                           SimpleAllToAllWiringMethod(net), 
                                           collectIDs = True)
        
        m.EI.proj = ConnectionsProjection( m.exc_nrn_popul, m.inh_nrn_popul, 
                                           syn_factory[EI],
                                           RandomConnections( p.EI.C),
                                           SimpleAllToAllWiringMethod(net), 
                                           collectIDs = True )
        
        m.IE.proj = ConnectionsProjection( m.inh_nrn_popul, m.exc_nrn_popul, 
                                           syn_factory[IE],
                                           RandomConnections( p.IE.C),
                                           SimpleAllToAllWiringMethod(net), 
                                           collectIDs = True )
        
        m.II.proj = ConnectionsProjection( m.inh_nrn_popul, m.inh_nrn_popul, 
                                           syn_factory[II],
                                           RandomConnections( p.II.C),
                                           SimpleAllToAllWiringMethod(net), 
                                           collectIDs = True )
        
        print "Total number of synapses is ", m.EE.proj.size() + m.EI.proj.size() + m.IE.proj.size() + m.II.proj.size()
        
        m.numSynapses = m.EE.proj.size() + m.EI.proj.size() + m.IE.proj.size() + m.II.proj.size()

    def reset(self):
        net = self.net     
        m = self.elements
        ep = self.expParams
           
        for i in range(m.EE.proj.size()):
            m.EE.proj.object(i).reset(ep.DTsim)
        for i in range(m.IE.proj.size()):
            m.IE.proj.object(i).reset(ep.DTsim)
        for i in range(m.EI.proj.size()):
            m.EI.proj.object(i).reset(ep.DTsim)
        for i in range(m.II.proj.size()):
            m.II.proj.object(i).reset(ep.DTsim)
        
        for id in m.all_nrn_popul.idVector():
            net.object(id).reset(ep.DTsim)
        
    def setupRecordings(self):
        ep = self.expParams
        m = self.elements
        p = self.params
        r = pcsim.Recordings(self.net)
        net = self.net
    
        # *********************************************************************************
        # SPIKE RECORDINGS        
        r.exc_spikes = m.exc_nrn_popul.record(SpikeTimeRecorder())        
        r.inh_spikes = m.inh_nrn_popul.record(SpikeTimeRecorder())
        
        r.numSynapses = m.numSynapses
        
        return r

    def scriptList(self):
        return ['LiquidModel400.py']
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using DHI.Mike.Install;
using DHI.MHydro.Data.WQ;
using DHI.MHydro.Data;

namespace ListHelper
{
    public static class MHydroListHelper
    {
        static MHydroListHelper()
        {
            MikeImport.SetupLatest(MikeProducts.MikeCore);
        }

        public static void AddParamLocation(WQData wqData, WQParamLocation wqParamLocation)
        {
            wqData.WQParamLocationList.Add(wqParamLocation);
        }

        public static void AddParamToLocation(WQParamLocation wqParamLocation, WQParam wqParam)
        {
            wqParamLocation.WQParamList.Add(wqParam);
        }

        public static void AddKinematicRoutingMethod(KinematicRoutingMethodListPfs kinematicRoutingMethodList, KinematicRoutingMethodPfs kinematicRoutingMethod)
        {
            kinematicRoutingMethodPfs kinMethod = new KinematicRoutingMethodPfs();

            kinematicRoutingMethodList.Add(kinematicRoutingMethod);
        }
    }
}

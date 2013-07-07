//
//  HoardersPythonExtension.h
//  Hoarders
//
//  Created by Sidd Sathyam on 6/30/13.
//  Copyright (c) 2013 Sidd Sathyam. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "HoardersConstants.h"

@interface HoardersPythonExtension : NSObject
	+ (HoardersPythonExtension*) sharedPythonObject;
	- (void) runInitScript;
	- (void) runDirChangeScriptWithPaths: (NSArray*) paths;
@end
